import inspect

from pathlib import Path
from typing import Any, Dict, List

from fastapi import FastAPI
from fastapi.routing import APIRoute
from pydantic import BaseModel
from sqlmodel import SQLModel


class CodeGenerator:
    """代码生成器主类"""

    def __init__(self, app: FastAPI):
        self.app = app
        self.template_dir = Path(__file__).parent / "templates"

    def get_routes_by_tag(self, tag: str) -> List[APIRoute]:
        """根据tag获取路由列表"""
        routes = []
        for route in self.app.routes:
            if isinstance(route, APIRoute):
                if tag in getattr(route, "tags", []):
                    routes.append(route)
        return routes

    def get_route_info(self, route: APIRoute) -> Dict[str, Any]:
        """获取路由详细信息"""
        return {
            "path": route.path,
            "method": route.methods,
            "name": route.name,
            "response_model": self._get_response_model(route),
            "parameters": self._get_parameters(route),
            "request_model": self._get_request_model(route)
        }

    def _get_response_model(self, route: APIRoute) -> SQLModel | BaseModel | None:
        """获取响应模型"""
        return getattr(route, "response_model", None)

    def _get_parameters(self, route: APIRoute) -> List[Dict[str, Any]]:
        """获取路由参数信息"""
        params = []
        sig = inspect.signature(route.endpoint)
        for name, param in sig.parameters.items():
            if name not in ["request", "response"]:
                # 获取实际类型
                param_type = param.annotation
                if hasattr(param_type, "__origin__") and str(param_type.__origin__) == "typing.Annotated":
                    param_type = param_type.__args__[0]

                params.append({
                    "name": name,
                    "annotation": param_type,
                    "default": None if param.default is inspect._empty else param.default
                })
        return params

    def _get_request_model(self, route: APIRoute) -> type[SQLModel | BaseModel] | None:
        """获取请求模型"""
        sig = inspect.signature(route.endpoint)
        for param in sig.parameters.values():
            if inspect.isclass(param.annotation) and issubclass(param.annotation, SQLModel | BaseModel):
                data = param.annotation
                return data
        return None
