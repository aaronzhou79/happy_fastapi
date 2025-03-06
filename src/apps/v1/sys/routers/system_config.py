# src/apps/v1/sys/routers/system_config.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Description: 系统配置路由

from fastapi import APIRouter
from pydantic import BaseModel

from src.common.constants import NumericFieldType, get_numeric_config_for_frontend
from src.core.responses.response_schema import ResponseModel, response_base

router = APIRouter(prefix="/system-config", tags=["系统配置"])


class NumericFieldConfig(BaseModel):
    """数值字段配置"""

    precision: int
    scale: int
    format: str
    symbol: str
    align: str
    defaultValue: str


class NumericFieldConfigResponse(BaseModel):
    """数值字段配置响应"""

    money: NumericFieldConfig
    weight: NumericFieldConfig
    area: NumericFieldConfig
    length: NumericFieldConfig
    quantity: NumericFieldConfig
    percentage: NumericFieldConfig
    exchange_rate: NumericFieldConfig
    price: NumericFieldConfig
    custom: NumericFieldConfig


@router.get("/numeric-field-config")
async def get_numeric_field_config() -> ResponseModel:
    """获取数值字段精度配置

    Returns:
        NumericFieldConfigResponse: 数值字段配置
    """
    config = get_numeric_config_for_frontend()
    data = NumericFieldConfigResponse(
        money=NumericFieldConfig(**config[NumericFieldType.MONEY]),
        weight=NumericFieldConfig(**config[NumericFieldType.WEIGHT]),
        area=NumericFieldConfig(**config[NumericFieldType.AREA]),
        length=NumericFieldConfig(**config[NumericFieldType.LENGTH]),
        quantity=NumericFieldConfig(**config[NumericFieldType.QUANTITY]),
        percentage=NumericFieldConfig(**config[NumericFieldType.PERCENTAGE]),
        exchange_rate=NumericFieldConfig(**config[NumericFieldType.EXCHANGE_RATE]),
        price=NumericFieldConfig(**config[NumericFieldType.PRICE]),
        custom=NumericFieldConfig(**config[NumericFieldType.CUSTOM]),
    )
    return response_base.success(data=data)
