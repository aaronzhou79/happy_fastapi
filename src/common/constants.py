# src/common/constants.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Description: 系统常量定义

from decimal import Decimal
from enum import Enum
from typing import Dict, Type

# 数值字段精度配置
class NumericFieldType(str, Enum):
    """数值字段类型"""
    # 金额
    MONEY = "money"
    # 重量
    WEIGHT = "weight"
    # 面积
    AREA = "area"
    # 长度
    LENGTH = "length"
    # 数量
    QUANTITY = "quantity"
    # 百分比
    PERCENTAGE = "percentage"
    # 汇率
    EXCHANGE_RATE = "exchange_rate"
    # 单价
    PRICE = "price"
    # 自定义
    CUSTOM = "custom"

# 数值字段精度配置
NUMERIC_PRECISION: Dict[NumericFieldType, Dict[str, int]] = {
    NumericFieldType.MONEY:         {"precision": 18, "scale": 2},  # 金额：  18位数字，2位小数
    NumericFieldType.WEIGHT:        {"precision": 15, "scale": 3},  # 重量：  15位数字，3位小数
    NumericFieldType.AREA:          {"precision": 15, "scale": 4},  # 面积：  15位数字，4位小数
    NumericFieldType.LENGTH:        {"precision": 15, "scale": 4},  # 长度：  15位数字，4位小数
    NumericFieldType.QUANTITY:      {"precision": 15, "scale": 4},  # 数量：  15位数字，4位小数
    NumericFieldType.PERCENTAGE:    {"precision": 5, "scale": 2},   # 百分比： 5位数字，2位小数
    NumericFieldType.EXCHANGE_RATE: {"precision": 10, "scale": 6},  # 汇率：  10位数字，6位小数
    NumericFieldType.PRICE:         {"precision": 18, "scale": 4},  # 单价：  18位数字，4位小数
    NumericFieldType.CUSTOM:        {"precision": 18, "scale": 6},  # 自定义：18位数字，6位小数
}

# 默认数值字段精度
DEFAULT_NUMERIC_TYPE = NumericFieldType.CUSTOM

# 数值字段默认值
DEFAULT_NUMERIC_VALUES: Dict[NumericFieldType, Decimal] = {
    NumericFieldType.MONEY: Decimal("0.00"),
    NumericFieldType.WEIGHT: Decimal("0.000"),
    NumericFieldType.AREA: Decimal("0.0000"),
    NumericFieldType.LENGTH: Decimal("0.00"),
    NumericFieldType.QUANTITY: Decimal("0.00"),
    NumericFieldType.PERCENTAGE: Decimal("0.00"),
    NumericFieldType.EXCHANGE_RATE: Decimal("1.000000"),
    NumericFieldType.PRICE: Decimal("0.0000"),
    NumericFieldType.CUSTOM: Decimal("0.000000"),
}

# 前端格式化配置
FRONTEND_FORMAT_CONFIG = {
    NumericFieldType.MONEY: {
        "format": "#,##0.00",  # 千分位分隔符，2位小数
        "symbol": "¥",  # 货币符号
        "align": "right",  # 对齐方式
    },
    NumericFieldType.WEIGHT: {
        "format": "#,##0.000",  # 千分位分隔符，3位小数
        "symbol": "kg",  # 单位
        "align": "right",
    },
    NumericFieldType.AREA: {
        "format": "#,##0.0000",  # 千分位分隔符，4位小数
        "symbol": "m²",  # 单位
        "align": "right",
    },
    NumericFieldType.LENGTH: {
        "format": "#,##0.00",  # 千分位分隔符，2位小数
        "symbol": "m",  # 单位
        "align": "right",
    },
    NumericFieldType.QUANTITY: {
        "format": "#,##0.00",  # 千分位分隔符，2位小数
        "symbol": "",  # 单位
        "align": "right",
    },
    NumericFieldType.PERCENTAGE: {
        "format": "0.00%",  # 百分比格式，2位小数
        "symbol": "",  # 单位
        "align": "right",
    },
    NumericFieldType.EXCHANGE_RATE: {
        "format": "#,##0.000000",  # 千分位分隔符，6位小数
        "symbol": "",  # 单位
        "align": "right",
    },
    NumericFieldType.PRICE: {
        "format": "#,##0.0000",  # 千分位分隔符，4位小数
        "symbol": "¥",  # 单位
        "align": "right",
    },
    NumericFieldType.CUSTOM: {
        "format": "#,##0.000000",  # 千分位分隔符，6位小数
        "symbol": "",  # 单位
        "align": "right",
    },
}

def get_numeric_config_for_frontend():
    """获取前端可用的数值字段配置

    Returns:
        dict: 包含所有数值字段类型的精度和格式化配置
    """
    config = {}
    for field_type in NumericFieldType:
        config[field_type] = {
            "precision": NUMERIC_PRECISION[field_type]["precision"],
            "scale": NUMERIC_PRECISION[field_type]["scale"],
            "format": FRONTEND_FORMAT_CONFIG[field_type]["format"],
            "symbol": FRONTEND_FORMAT_CONFIG[field_type]["symbol"],
            "align": FRONTEND_FORMAT_CONFIG[field_type]["align"],
            "defaultValue": str(DEFAULT_NUMERIC_VALUES[field_type]),
        }
    return config