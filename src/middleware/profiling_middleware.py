import cProfile
import pstats
import time
import tracemalloc

from io import StringIO
from typing import List, Tuple

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from src.common.logger import log
from src.core.conf import settings


class ProfilingMiddleware(BaseHTTPMiddleware):
    """性能分析中间件"""

    SLOW_THRESHOLD = 0.1  # 慢请求阈值(秒)
    DB_OP_KEYWORDS = ('select', 'insert', 'update', 'delete', 'commit', 'rollback')

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # 启动内存跟踪
        tracemalloc.start()

        # 启动性能分析
        profiler = cProfile.Profile()
        profiler.enable()

        # 记录开始时间
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time

        # 停止性能分析
        profiler.disable()

        # 获取内存快照
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # 分析性能数据
        s = StringIO()
        stats = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
        stats.print_stats()

        # 解析性能数据
        profile_data = self._parse_profile_data(s.getvalue())

        # 记录性能日志
        self._log_performance_data(
            request=request,
            duration=duration,
            profile_data=profile_data,
            current_memory=current,
            peak_memory=peak
        )

        return response

    def _parse_profile_data(self, profile_text: str) -> List[Tuple[str, float, int]]:
        """解析性能数据,返回[(函数名,耗时,调用次数)]"""
        results = []
        for line in profile_text.split('\n'):
            if any(kw in line.lower() for kw in self.DB_OP_KEYWORDS):
                try:
                    # 解析pstats输出的性能数据行
                    parts = line.strip().split()
                    if len(parts) >= 6:
                        time_per_call = float(parts[3])
                        total_calls = int(parts[0])
                        func_name = parts[5]
                        results.append((func_name, time_per_call, total_calls))
                except (IndexError, ValueError):
                    continue
        return results

    def _log_performance_data(
        self,
        request: Request,
        duration: float,
        profile_data: List[Tuple[str, float, int]],
        current_memory: int,
        peak_memory: int
    ) -> None:
        """记录性能数据"""
        # 基础信息
        log.info("=================== 性能分析 ===================")
        log.info("请求路由: {} {}", request.method, request.url.path)
        log.info("请求耗时: {:.3f}s", duration)

        # 慢请求警告
        if duration > self.SLOW_THRESHOLD:
            log.warning("⚠️ 慢请求检测! 耗时: {:.3f}s", duration)

        # 内存使用
        log.info("内存使用: 当前={:.2f}MB, 峰值={:.2f}MB",
                current_memory / 1024 / 1024,
                peak_memory / 1024 / 1024)

        # 数据库操作统计
        if profile_data:
            log.info("------------------ 数据操作 ------------------")
            # 按总执行时间排序并只取前10条
            sorted_data = sorted(
                profile_data,
                key=lambda x: x[1] * x[2],
                reverse=True
            )[:10]

            for func_name, time_per_call, total_calls in sorted_data:
                short_name = func_name.split('/')[-1]
                total_time = time_per_call * total_calls
                percentage = (total_time / duration) * 100 if duration > 0 else 0
                log.info("{}: {:.3f}s ({:.1f}%) [调用次数={}]",
                        short_name, total_time, percentage, total_calls)

        # 总执行时间
        total_execution_time = sum(time_per_call * total_calls for _, time_per_call, total_calls in profile_data)
        log.info("总执行时间: {:.3f}s", total_execution_time)
        log.info("=======================================================")
