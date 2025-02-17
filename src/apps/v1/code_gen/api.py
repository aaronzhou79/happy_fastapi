import inspect

from enum import Enum
from typing import Any, Dict, Generic, List, Set, Type, Union, get_args, get_origin

from fastapi import APIRouter, Request
from fastapi.routing import APIRoute
from pydantic import BaseModel
from sqlmodel import SQLModel

from src.core.responses.response_schema import ResponseModel

from .generator import CodeGenerator
from .type_mapper import TypeMapper

router = APIRouter(prefix="/code-gen", tags=["代码生成"])


def extract_pydantic_models(type_annotation: Any) -> Set[Type[Union[BaseModel, Enum]]]:
    """递归提取类型中的所有Pydantic模型和枚举类型"""
    models = set()

    # 处理None类型
    if type_annotation is None:
        return models

    # 处理ResponseModel类型
    if (inspect.isclass(type_annotation) and
        hasattr(type_annotation, "__bases__") and
        ResponseModel in type_annotation.__bases__):
        # 从data属性的类型注解中获取实际类型
        if hasattr(type_annotation, "model_fields"):
            data_type = type_annotation.model_fields.get("data").annotation
            if data_type:
                models.update(extract_pydantic_models(data_type))
        return models

    # 如果是BaseModel子类,直接添加
    if inspect.isclass(type_annotation) and issubclass(type_annotation, BaseModel):
        models.add(type_annotation)
        return models

    # 处理枚举类型
    if inspect.isclass(type_annotation) and issubclass(type_annotation, Enum):
        models.add(type_annotation)
        return models

    # 获取原始类型和类型参数
    origin = get_origin(type_annotation)
    args = get_args(type_annotation)

    # 如果有原始类型,处理类型参数
    if origin is not None:
        # 处理Union类型
        if origin is Union:
            for arg in args:
                models.update(extract_pydantic_models(arg))
        # 处理容器类型(List, Dict等)
        else:
            for arg in args:
                models.update(extract_pydantic_models(arg))

    return models

@router.get("/generate")
async def generate_code(request: Request, tag: str) -> Dict[str, Any]:
    """根据tag生成前端代码"""
    generator = CodeGenerator(request.app)
    routes = generator.get_routes_by_tag(tag)

    result = {
        "types": [],  # TypeScript类型定义
        "api": [],    # API请求代码
        "components": []  # Vue组件
    }

    # 收集所有用到的模型
    models = set()
    for route in routes:
        info = generator.get_route_info(route)

        # 处理响应模型
        if info["response_model"]:
            models.update(extract_pydantic_models(info["response_model"]))

        # 处理请求参数
        if info["parameters"]:
            for param in info["parameters"]:
                if param["annotation"]:
                    models.update(extract_pydantic_models(param["annotation"]))

    # 生成类型定义
    for model in models:
        if inspect.isclass(model) and issubclass(model, Enum):
            result["types"].append(TypeMapper.enum_to_definition(model))
        else:
            result["types"].append(TypeMapper.model_to_interface(model))

    # 生成API请求代码
    for route in routes:
        info = generator.get_route_info(route)
        result["api"].append(generate_api_code(info))

    # 生成Vue组件
    result["components"].extend(generate_vue_components(routes))

    return result


def generate_api_code(route_info: Dict[str, Any]) -> str:
    """生成API请求代码"""
    # 从methods set中获取第一个方法并转换为小写
    method = next(iter(route_info["method"])).lower()
    path = route_info["path"]
    name = route_info["name"]

    params = []
    if route_info["request_model"]:
        params.append(f"data: {route_info['request_model'].__name__}")

    response_type = "void"
    if route_info["response_model"]:
        response_type = route_info["response_model"].__name__

    return f"""
        export const {name} = async ({', '.join(params)}): Promise<{response_type}> => {{
        const response = await axios.{method}('{path}'{', data' if params else ''});
        return response.data;
        }};
        """


def generate_vue_components(routes: List[APIRoute]) -> List[str]:
    """生成Vue组件代码"""
    components = []
    # TODO: 根据路由生成对应的Vue组件
    return components