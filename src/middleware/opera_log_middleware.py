#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from asyncio import create_task

from asgiref.sync import sync_to_async
from fastapi import Response
from starlette.datastructures import UploadFile
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request

from src.apps.v1.sys.models.opera_log import OperaLogCreate
from src.apps.v1.sys.service.opera_log import svr_opera_log
from src.common.dataclasses import RequestCallNext
from src.common.enums import OperaLogCipher, OperaLogStatus
from src.common.logger import log
from src.core.conf import settings
from src.utils.encrypt import AESCipher, ItsDCipher, Md5Cipher
from src.utils.timezone import TimeZone
from src.utils.trace_id import get_request_trace_id


class OperaLogMiddleware(BaseHTTPMiddleware):
    """操作日志中间件"""

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        操作日志中间件

        :param request:
        :param call_next:
        :return:
        """
        # 排除记录白名单
        path = request.url.path
        if path in settings.OPERA_LOG_PATH_EXCLUDE or not path.startswith(f'{settings.API_PATH}'):
            return await call_next(request)

        # 此信息依赖于 jwt 中间件
        if hasattr(request.state, 'user') and hasattr(request.state.user, 'username'):
            username = getattr(request.state.user, 'username', '-')
        else:
            username = '-'
        method = request.method
        args = await self.get_request_args(request)
        args = await self.desensitization(args)

        # 执行请求
        start_time = TimeZone.now()
        request_next = await self.execute_request(request, call_next)
        end_time = TimeZone.now()
        cost_time = (end_time - start_time).total_seconds() * 1000.0

        # 此信息只能在请求后获取
        _route = request.scope.get('route')
        summary = getattr(_route, 'summary', None) or ''

        # 日志创建
        opera_log_in = OperaLogCreate(
            trace_id=get_request_trace_id(request),                 # type: ignore
            username=username,                                      # type: ignore
            method=method,                                          # type: ignore
            title=summary,                                          # type: ignore
            path=path,                                              # type: ignore
            ip=getattr(request.state, 'ip', '-'),                   # type: ignore
            country=getattr(request.state, 'country', '-'),         # type: ignore
            region=getattr(request.state, 'region', '-'),           # type: ignore
            city=getattr(request.state, 'city', '-'),               # type: ignore
            user_agent=getattr(request.state, 'user_agent', '-'),   # type: ignore
            os=getattr(request.state, 'os', '-'),                   # type: ignore
            browser=getattr(request.state, 'browser', '-'),         # type: ignore
            device=getattr(request.state, 'device', '-'),           # type: ignore
            args=args,                                              # type: ignore
            status=request_next.status,                             # type: ignore
            code=str(request_next.code),                            # type: ignore
            msg=request_next.msg,                                   # type: ignore
            cost_time=cost_time,                                    # type: ignore
            opera_time=start_time,                                  # type: ignore
        )

        create_task(svr_opera_log.create_opera_log(opera_log_in))

        # 错误抛出
        err = request_next.err
        if err:
            raise err from None

        return request_next.response

    async def execute_request(self, request: Request, call_next: RequestResponseEndpoint) -> RequestCallNext:
        """执行请求"""
        code = 200
        msg = 'Success'
        status = OperaLogStatus.SUCCESS
        err = None
        response = None
        try:
            response = await call_next(request)
            code, msg = self.request_exception_handler(request, code, msg)
        except Exception as e:
            log.error(f'请求异常: {e}')
            # code 处理包含 SQLAlchemy 和 Pydantic
            code = getattr(e, 'code', None) or code
            msg = getattr(e, 'msg', None) or msg
            status = OperaLogStatus.FAIL
            err = e

        # 确保 response 不为 None
        if response is None:
            response = Response(content="An error occurred", status_code=500)

        return RequestCallNext(code=code, msg=msg, status=status, err=err, response=response)

    @staticmethod
    def request_exception_handler(request: Request, code: int, msg: str) -> tuple[int, str]:
        """请求异常处理器"""
        exception_states = [
            '__request_http_exception__',
            '__request_validation_exception__',
            '__request_pydantic_user_error__',
            '__request_assertion_error__',
            '__request_custom_exception__',
            '__request_all_unknown_exception__',
            '__request_cors_500_exception__',
        ]
        for state in exception_states:
            exception = getattr(request.state, state, None)
            if exception:
                code = exception.get('code')
                msg = exception.get('msg')
                log.error(f'请求异常: {msg}')
                break
        return code, msg

    @staticmethod
    async def get_request_args(request: Request) -> dict:
        """获取请求参数"""
        args = dict(request.query_params)
        args.update(request.path_params)
        # Tip: .body() 必须在 .form() 之前获取
        # https://github.com/encode/starlette/discussions/1933
        body_data = await request.body()
        form_data = await request.form()
        if form_data:
            args.update(
                {k: v.filename if isinstance(v, UploadFile) else v for k, v in form_data.items()}  # type: ignore
            )  # type: ignore
        else:
            if body_data:
                json_data = await request.json()
                if not isinstance(json_data, dict):
                    json_data = {
                        f'{type(json_data)}_to_dict_data': json_data.decode('utf-8')
                        if isinstance(json_data, bytes)
                        else json_data
                    }
                args.update(json_data)
        return args


    @staticmethod
    @sync_to_async
    def desensitization(args: dict) -> dict | None:
        """脱敏处理"""
        if not args:
            return {}

        def _encrypt_value(value: str, cipher_type: OperaLogCipher) -> str:
            """加密单个值"""
            encrypt_map = {
                OperaLogCipher.AES: lambda x: (AESCipher(settings.OPERA_LOG_ENCRYPT_SECRET_KEY).encrypt(x)).hex(),
                OperaLogCipher.MD5: Md5Cipher.encrypt,
                OperaLogCipher.ITSDANGEROUS: lambda x: ItsDCipher(settings.OPERA_LOG_ENCRYPT_SECRET_KEY).encrypt(x),
                OperaLogCipher.PLAN: lambda x: x,
            }
            return encrypt_map.get(cipher_type, lambda _: '******')(value)
        for key in args.keys():
            if key in settings.OPERA_LOG_ENCRYPT_KEY_INCLUDE:
                args[key] = _encrypt_value(args[key], OperaLogCipher(settings.OPERA_LOG_ENCRYPT_TYPE))
        return args
