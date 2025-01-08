import cProfile
import pstats
import time
import tracemalloc

from typing import List

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from src.common.logger import log
from src.core.conf import settings


class ProfilingMiddleware(BaseHTTPMiddleware):
    """性能分析中间件"""

    DB_OP_KEYWORDS = ('query', 'insert', 'update', 'delete', 'commit', 'rollback', 'execute')

    def __init__(self, app, **options):   # noqa: ANN001
        """
        初始化
        """
        super().__init__(app)
        self._profiler = None
        # 从配置或参数中读取阈值
        self.slow_threshold = options.get('slow_threshold', settings.SLOW_REQUEST_THRESHOLD)
        self.memory_warning_threshold = options.get(
            'memory_warning_threshold',
            settings.MEMORY_WARNING_THRESHOLD)
        # 启动内存跟踪(只需启动一次)
        tracemalloc.start()

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """
        处理请求
        """
        # 获取请求ID用于关联日志
        request_id = request.headers.get('X-Request-ID', '')
        if self._profiler is not None:
            # 如果已经有profiler在运行，直接执行下一个中间件
            return await call_next(request)
        # 启动性能分析
        self._profiler = cProfile.Profile()
        self._profiler.enable()

        # 记录开始时间和内存
        start_time = time.time()
        start_memory = tracemalloc.get_traced_memory()[0]

        response = await call_next(request)

        # 计算耗时和内存变化
        duration = time.time() - start_time
        current_memory, peak_memory = tracemalloc.get_traced_memory()
        memory_increase = current_memory - start_memory

        # 停止性能分析
        self._profiler.disable()

        # 使用 Stats 对象直接获取性能数据,避免字符串解析
        stats = pstats.Stats(self._profiler)
        profile_data = self._get_profile_stats(stats)

        # 记录结构化的性能日志
        self._log_performance_data(
            request=request,
            request_id=request_id,
            duration=duration,
            profile_data=profile_data,
            memory_increase=memory_increase,
            peak_memory=peak_memory
        )

        return response

    def _get_profile_stats(self, stats: pstats.Stats) -> List[dict]:
        """直接从 Stats 对象获取性能数据"""
        results = []
        for func, (cc, nc, tt, ct, callers) in stats.stats.items():   # type: ignore
            if any(kw in str(func).lower() for kw in self.DB_OP_KEYWORDS):
                results.append({
                    'func_name': func[2],
                    'total_time': ct,
                    'calls': cc
                })
        return results

    def _log_performance_data(
        self,
        request: Request,
        request_id: str,
        duration: float,
        profile_data: List[dict],
        memory_increase: int,
        peak_memory: int
    ) -> None:
        """记录结构化的性能数据"""
        perf_data = {
            'request_id': request_id,
            'path': f"{request.method} {request.url.path}",
            'duration': round(duration, 3),
            'memory': {
                'increase': round(memory_increase / 1024 / 1024, 2),
                'peak': round(peak_memory / 1024 / 1024, 2)
            },
            'db_operations': []
        }

        # 添加警告标记
        if duration > self.slow_threshold:
            perf_data['warnings'] = ['slow_request']
        if memory_increase > self.memory_warning_threshold:
            perf_data['warnings'] = perf_data.get('warnings', []) + ['high_memory']

        # 处理数据库操作数据
        if profile_data:
            sorted_data = sorted(profile_data, key=lambda x: x['total_time'], reverse=True)[:10]
            for op in sorted_data:
                perf_data['db_operations'].append({
                    'name': op['func_name'].split('/')[-1],
                    'time': round(op['total_time'], 3),
                    'calls': op['calls'],
                    'percentage': round((op['total_time'] / duration) * 100, 1)
                })

        # 输出 JSON 格式日志
        log.info("--------------------------------")
        log.info(f"Performance Profile: {perf_data}")
