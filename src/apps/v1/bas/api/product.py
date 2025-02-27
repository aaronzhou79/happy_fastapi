# src/apps/v1/bas/api/product.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025-02-12
# @Author  : lei
# @File    : product.py
# @Software: Cursor
# @Description: 产品信息API

from fastapi import BackgroundTasks, Body, Depends, Request, Response

from src.apps.v1.bas.models.mdl_product import Product, ProductBase, ProductCreate, ProductUpdate
from src.apps.v1.bas.service.svr_product import svr_product
from src.common.base_api import BaseAPI
from src.core.responses.response_schema import ResponseModel, response_base
from src.core.security.auth_security import DependsJwtAuth
from src.core.security.permission import RequestPermission
from src.database.db_session import CurrentSession, async_audit_session, async_session

product_api = BaseAPI(
    module_name="bas",
    model=Product,
    service=svr_product,
    create_schema=ProductCreate,
    update_schema=ProductUpdate,
    base_schema=ProductBase,
    prefix="/product",
    gen_bulk_create=True,
    gen_bulk_delete=True,
    gen_delete=True,
    tags=["基础管理/产品信息"],
)


# @product_api.router.post(
#     "/cust_create",
#     description="自定义新增, basic:product:cust_create",
#     dependencies=[
#         DependsJwtAuth,
#         Depends(RequestPermission("basic:product:cust_create"))
#     ]
# )
# async def cust_create(product: ProductCreate, request: Request
# ) -> ResponseModel:
#     """自定义新增产品"""
#     async with async_audit_session(async_session(), request) as session:
#         data = await svr_product.cust_create(session, product)
#         return response_base.success(data=data)

@product_api.router.get(
    "/get_boms",
    dependencies=[
        DependsJwtAuth
    ]
)
async def get_boms(session: CurrentSession, product_id: int) -> ResponseModel:
    """根据产品Id获取Boms"""
    data = await svr_product.get_product_boms(session, product_id)
    return response_base.success(data=data)


@product_api.router.get(
    "/get_by_code",
    dependencies=[
        DependsJwtAuth
    ]
)
async def get_by_code(session: CurrentSession, code: str) -> ResponseModel:
    """根据产品Code获取Boms"""
    data = await svr_product.get_product(session, code)
    return response_base.success(data=data.to_tree_dict())