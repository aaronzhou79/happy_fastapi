# src/apps/v1/bas/service/svr_product.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2025-02-12
# @Author  : lei
# @File    : svr_product.py
# @Software: Cursor
# @Description: 产品信息服务

from typing import Sequence, override

from src.apps.v1.bas.crud.crud_product import crud_product
from src.apps.v1.bas.crud.crud_product_bom import crud_bom
from src.apps.v1.bas.crud.crud_product_bom_wip import crud_wip
from src.apps.v1.bas.models.mdl_product import Product, ProductCreate, ProductUpdate
from src.apps.v1.bas.models.mdl_product_bom import ProductBom
from src.common.base_crud import HookContext
from src.common.base_service import BaseService
from src.common.enums import HookTypeEnum
from src.common.enums import ProductBomType as BomType
from src.core.exceptions import errors
from src.database.db_session import AuditAsyncSession
from src.utils.snowflake import id_worker


class SvrProduct(BaseService[Product, ProductCreate, ProductUpdate]):
    """
    产品信息服务
    """
    rule = 0
    letters = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N",
        "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]

    def __init__(self):
        self.crud = crud_product

        # Register hook
        self.add_hook(HookTypeEnum.before_create, self._handle_code)
        self.add_hook(HookTypeEnum.before_update, self._handle_code)

    async def _handle_code(self, context: HookContext) -> HookContext:
        """编码赋值"""
        obj_in = context.params['obj_in']
        session = context.session
        product_id = 0

        if obj_in.code:
            pass  # 如果有编号则保持不变
        else:
            obj_in.code = "自动生成"

        if hasattr(obj_in, "id"):
            product_id = obj_in.id

        product = await crud_product.get_product(session, obj_in.code, product_id)

        if product:
            raise errors.RequestError(data=f"产品 [{product.name}] 已使用编码 {product.code}")

        return context

    async def get_product(self, session: AuditAsyncSession, product_code: str) -> Product:
        """
        根据产品编码获取产品

        :param product_code: 产品编码
        :return: 相同编码的产品
        """
        return await crud_product.get_product(session, product_code)

    async def get_product_boms(self, session: AuditAsyncSession, product_id: int) -> Sequence[ProductBom]:
        """
        根据产品Id获取产品Boms

        :param product_id: 产品Id
        :return: 产品Boms
        """
        boms = list(await crud_product.get_product_boms(session, product_id))
        wips = list(await crud_product.get_product_wips(session, product_id))

        for bom in boms:
            for wip in wips:
                if bom.id == wip.bom_id:
                    bom.wips.append(wip)

        return boms

    def set_root_bom(self, product: Product, root_bom: ProductBom) -> Product:
        """设置根BOM信息"""
        root_bom.id = id_worker.get_id()
        root_bom.product_id = product.id  # 关联产品ID
        root_bom.parent_id = product.id  # 关联父子集
        root_bom.level = 0  # bom层级
        root_bom.is_setting = True  # 默认成品层需要设置
        root_bom.composite = product.composite

        # 处理工序
        for wip_seq_no, wip in enumerate(root_bom.wips, 1):
            wip.id = id_worker.get_id()
            wip.product_id = product.id
            wip.bom_id = root_bom.id
            wip.seq_no = wip_seq_no
            product.wips.append(wip)

        root_bom.wip_codes = "-->".join(wip.code for wip in sorted(root_bom.wips, key=lambda x: x.seq_no))
        root_bom.wip_names = "-->".join(wip.name for wip in sorted(root_bom.wips, key=lambda x: x.seq_no))
        root_bom.composite = product.composite

        # 加入根节点
        product.boms.append(root_bom)

        # 递归设置bom层
        self.set_product_bom(product, root_bom)

        # 防止复合厚度出错，重新计算
        if product.composite:
            product.product_deep = sum(bom.material_deep for bom in product.boms if not bom.composite)
            product.rm_deep = sum(bom.material_deep for bom in product.boms
                                if bom.type == BomType.SMG and not bom.composite)
            product.film_deep = sum(bom.material_deep for bom in product.boms
                                  if bom.type == BomType.JJ)
            product.al_bar_deep = sum(bom.material_deep for bom in product.boms
                                    if bom.type == BomType.ZK)
            # 获取所有SMG类型的子BOM
            smg_boms = [bom for bom in root_bom.children if bom.type == BomType.SMG]
            # 递归设置片标记（复合玻璃才需要）
            self.set_bom_flag(smg_boms)

            self.sync_product_boms_deep(product)

        return product

    def set_product_bom(self, product: Product, bom: ProductBom) -> Product:
        """
        设置产品Bom信息，递归处理BOM结构

        Args:
            product: 产品对象
            bom: 产品BOM对象

        Returns:
            Product: 处理后的产品对象
        """
        for item in bom.children:
            item.id = id_worker.get_id()
            item.product_id = product.id  # 关联产品ID
            item.parent_id = bom.id  # 关联父子集
            wip_seq_no = 0

            for wip in item.wips:
                wip_seq_no += 1
                wip.id = id_worker.get_id()
                wip.product_id = product.id  # 关联产品ID
                wip.bom_id = item.id  # 关联BomID
                wip.seq_no = wip_seq_no

                product.boms.append(item)

            item.level = bom.level + 1
            item.composite = len(item.children) > 0

            product.boms.append(item)

            # 如果当前BOM项有子项，递归处理
            if item.children:
                self.set_product_bom(product, item)

        return product

    def set_bom_flag(self, boms: list[ProductBom], flag: str = "") -> list[ProductBom]:
        """设置BOM标识"""
        if self.rule == 0:  # 手动设置，不处理
            return boms

        if self.rule == 2:  # 整数递增
            seq_no = 1
            for bom in boms:
                if bom.type == BomType.SMG:
                    bom.flag = f"{flag}.{seq_no}" if flag else str(seq_no)
                    self.set_bom_flag(bom.children, bom.flag)
                    seq_no += 1

        elif self.rule == 3:  # 字母递增
            seq_no = 1
            index = 0
            for bom in boms:
                if bom.type == BomType.SMG:
                    bom.flag = f"{flag}.{seq_no}" if flag else self.letters[index]
                    self.set_bom_flag(bom.children, bom.flag)
                    seq_no += 1
                    index += 1

        return boms

    def sync_product_boms_deep(self, product: Product) -> None:
        """同步计算产品BOM深度"""
        max_level = max(bom.level for bom in product.boms)

        # 从底层向上计算
        for level in range(max_level - 1, -1, -1):
            composite_boms = [bom for bom in product.boms
                            if bom.level == level and len(bom.children) > 0]

            for item in composite_boms:
                item.material_deep = sum(child.material_deep for child in item.children)

        # 设置产品深度
        root_bom = next((bom for bom in product.boms if bom.level == 0), None)
        product.product_deep = root_bom.material_deep if root_bom else 0
        product.rm_deep = sum(bom.material_deep for bom in product.boms
                            if bom.type == BomType.SMG and not bom.composite)
        product.al_bar_deep = sum(bom.material_deep for bom in product.boms
                                if bom.type == BomType.ZK)
        product.film_deep = sum(bom.material_deep for bom in product.boms
                              if bom.type == BomType.JJ)

    def sync_product_name(self, product: Product) -> None:
        """同步计算产品名称"""
        max_level = max(bom.level for bom in product.boms)

        # 从底层向上计算
        for level in range(max_level - 1, -1, -1):
            composite_boms = [bom for bom in product.boms
                            if bom.level == level and len(bom.children) > 0]

            for item in composite_boms:
                item.material_code = "+".join(child.material_code for child in item.children)
                item.material_name = "+".join(child.material_name for child in item.children)

        # 设置产品编号和名称
        root_bom = next((bom for bom in product.boms if bom.level == 0), None)
        if root_bom and product.code:
            root_bom.material_code = product.code
        product.name = root_bom.material_name if root_bom else ""

    def validate(self, product: Product) -> None:
        """验证产品数据"""
        if not product.boms:
            raise errors.RequestError(message="请求参数错误！")

        if any(bom.is_setting and not bom.wip_codes for bom in product.boms):
            raise errors.RequestError(message="工序设置为 '是' 时，必须选填工艺！")

        if len(product.boms) == 1 and product.composite:
            raise errors.RequestError(message="当前产品BOM不符合复合产品规范！")

    # @override
    # async def create(self, session: AuditAsyncSession, obj_in: ProductCreate) -> Product:
    #     """
    #     自定义新增

    #     :param obj_in: 创建模型（参数名换成其它的，钩子里面也要同步处理，建议就使用该参数名称）
    #     """
    #     obj_in.id = id_worker.get_id()
    #     root_bom = obj_in.boms[0]  # 提取根BOM
    #     obj_in.boms.clear()
    #     obj_in.wips.clear()

    #     self.set_root_bom(obj_in, root_bom)
    #     self.validate(obj_in)

    #     return await self.crud.cust_create(session, obj_in, obj_in.boms, obj_in.wips)

    # @override
    # async def update(self, session: AuditAsyncSession, obj_in: ProductUpdate) -> Product:
    #     """
    #     自定义修改

    #     :param obj_in: 创建模型（参数名换成其它的，钩子里面也要同步处理，建议就使用该参数名称）
    #     """
    #     root_bom = obj_in.boms[0]  # 提取根BOM
    #     obj_in.boms.clear()
    #     obj_in.wips.clear()

    #     self.set_root_bom(obj_in, root_bom)
    #     self.validate(obj_in)

    #     return await self.crud.cust_update(session, obj_in, obj_in.boms, obj_in.wips)


svr_product = SvrProduct()
