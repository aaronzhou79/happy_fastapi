import json

from datetime import datetime
from typing import Any, Sequence

from sqlalchemy import select, text

from src.common.base_crud import CreateModelType, CRUDBase, UpdateModelType
from src.common.tree_model import TreeModel
from src.core.conf import settings
from src.core.exceptions import errors
from src.database.db_redis import redis_client
from src.database.db_session import AuditAsyncSession


class TreeJSONEncoder(json.JSONEncoder):
    """自定义JSON编码器,支持日期时间序列化"""
    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def datetime_parser(dct: dict) -> dict:
    """JSON解码器的自定义解析器,支持日期时间反序列化"""
    for k, v in dct.items():
        if isinstance(v, str):
            try:
                dct[k] = datetime.fromisoformat(v)
            except ValueError:
                pass
    return dct


class TreeCRUD(CRUDBase[TreeModel, CreateModelType, UpdateModelType]):
    """树形结构CRUD基类"""

    async def _update_node_path(
        self,
        session: AuditAsyncSession,
        node: TreeModel,
        parent: TreeModel | None = None
    ) -> None:
        """更新节点路径"""
        if parent is None:
            node.path = f"/{node.id}/"  # type: ignore[attr-defined]
            node.level = 1
            node.parent_id = None
        else:
            node.path = f"{parent.path}{node.id}/"  # type: ignore[attr-defined]
            node.level = parent.level + 1
            node.parent_id = parent.id   # type: ignore[attr-defined]

    async def _update_children_path(
        self,
        session: AuditAsyncSession,
        node: TreeModel
    ) -> None:
        """递归更新所有子节点的路径"""
        children = await node.get_children(session)
        for child in children:
            await self._update_node_path(session, child, node)
            session.add(child)
            await self._update_children_path(session, child)

    async def _check_cycle(
        self,
        session: AuditAsyncSession,
        node: TreeModel,
        new_parent_id: int
    ) -> bool:
        """检查是否会形成循环引用"""
        if node.id == new_parent_id:  # type: ignore[attr-defined]
            return True

        new_parent = await self.get_by_id(session, new_parent_id)
        if not new_parent:
            return False

        ancestors = await new_parent.get_ancestors(session)
        return any(a.id == node.id for a in ancestors)  # type: ignore[attr-defined]

    async def create(
        self,
        session: AuditAsyncSession,
        *,
        obj_in: CreateModelType | dict
    ) -> TreeModel:
        """创建节点"""
        if isinstance(obj_in, dict):
            create_data = obj_in
        else:
            create_data = obj_in.model_dump()

        parent_id = create_data.get("parent_id")
        if parent_id:
            parent = await self.get_by_id(session, parent_id)
            if not parent:
                raise errors.RequestError(data={"父节点不存在"})

        db_obj = await super().create(session, obj_in=create_data)
        await self._clear_tree_cache(session, db_obj)

        # 更新路径
        if parent_id:
            await self._update_node_path(session, db_obj, parent)
        else:
            await self._update_node_path(session, db_obj)

        session.add(db_obj)
        await session.flush()

        return db_obj

    async def update(
        self,
        session: AuditAsyncSession,
        *,
        obj_in: UpdateModelType | dict
    ) -> TreeModel:
        """更新节点"""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        db_obj = await self.get_by_id(session, update_data["id"])
        if not db_obj:
            raise errors.RequestError(data={"节点不存在"})

        # 检查是否更新了父节点
        new_parent_id = update_data.get("parent_id")
        if new_parent_id is not None and new_parent_id != db_obj.parent_id:
            # 检查循环引用
            if await self._check_cycle(session, db_obj, new_parent_id):
                raise errors.RequestError(data={"不能将节点移动到其子节点下"})

            # 更新节点路径
            if new_parent_id:
                new_parent = await self.get_by_id(session, new_parent_id)
                if not new_parent:
                    raise errors.RequestError(data={"父节点不存在"})
                await self._update_node_path(session, db_obj, new_parent)
            else:
                await self._update_node_path(session, db_obj)

            # 更新所有子节点的路径
            await self._update_children_path(session, db_obj)

        db_obj = await super().update(session, obj_in=update_data)
        await self._clear_tree_cache(session, db_obj)

        return db_obj

    async def delete(self, session: AuditAsyncSession, id: int) -> None:
        """删除节点及其所有子节点"""
        node = await self.get_by_id(session, id)
        if not node:
            raise errors.RequestError(data={"节点不存在"})

        # 删除所有子节点
        stmt = select(self.model).where(
            text(f"path LIKE '{node.path}%'")
        )
        result = await session.execute(stmt)
        children = result.scalars().all()

        for child in children:
            await session.delete(child)

        await self._clear_tree_cache(session, node)
        await super().delete(session, id)

    async def to_tree_dict(
        self,
        nodes: Sequence[TreeModel]
    ) -> Sequence[dict]:
        """将节点列表转换为树形结构字典"""
        # 按ID组织节点
        node_map: dict[int, dict] = {}
        root_nodes: list[dict] = []

        # 第一次遍历: 创建所有节点的字典表示
        for node in nodes:
            # 转换为字典并添加children字段
            node_dict = node.model_dump(exclude={'_sa_instance_state'})
            node_dict['children'] = []
            node_map[node.id] = node_dict  # type: ignore[attr-defined]

        # 第二次遍历: 构建树形结构
        for node in nodes:
            node_dict = node_map[node.id]  # type: ignore[attr-defined]
            if node.parent_id and node.parent_id in node_map:
                # 如果有父节点，添加到父节点的children中
                parent_dict = node_map[node.parent_id]
                parent_dict['children'].append(node_dict)
            else:
                # 如果没有父节点或父节点不在当前集合中，作为根节点
                root_nodes.append(node_dict)

        return root_nodes

    async def get_tree(
        self,
        session: AuditAsyncSession,
        root_id: int | None = None,
        max_depth: int = -1
    ) -> Sequence[dict]:
        """获取树形结构(带缓存)"""
        # 生成缓存key
        cache_key = (
            f"{settings.REDIS_CACHE_KEY_PREFIX}:{self.model.__name__}:tree:"
            f"{'root' if root_id is None else f'node:{root_id}'}"
            f":depth:{max_depth}"
        )

        # 尝试从缓存获取
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            try:
                # 使用自定义解析器反序列化
                return json.loads(cached_data, object_hook=datetime_parser)
            except Exception as e:
                print(f"反序列化缓存数据失败: {str(e)}")
                # 发生错误时从数据库重新获取

        # 从数据库获取扁平结构
        nodes = await self._get_tree_from_db(session, root_id, max_depth)

        # 转换为树形结构
        tree_data = await self.to_tree_dict(nodes)

        try:
            # 缓存树形结构
            await redis_client.set(
                cache_key,
                json.dumps(tree_data, cls=TreeJSONEncoder),
                ex=settings.CACHE_TREE_EXPIRE_IN_SECONDS
            )
        except Exception as e:
            print(f"序列化缓存数据失败: {str(e)}")

        return tree_data

    async def _get_tree_from_db(
        self,
        session: AuditAsyncSession,
        root_id: int | None = None,
        max_depth: int = -1
    ) -> Sequence[TreeModel]:
        """从数据库获取树形结构"""
        # 构建基础查询
        if root_id:
            # 如果指定了root_id，获取该节点及其所有子节点
            root = await self.get_by_id(session, root_id)
            if not root:
                return []
            stmt = select(self.model).where(
                text(f"path LIKE '{root.path}%'")  # type: ignore[attr-defined]
            )
            if max_depth > 0:
                stmt = stmt.where(
                    self.model.level <= root.level + max_depth  # type: ignore[attr-defined]
                )
        else:
            # 否则获取所有节点
            stmt = select(self.model)
            if max_depth > 0:
                stmt = stmt.where(
                    self.model.level <= max_depth  # type: ignore[attr-defined]
                )

        # 添加排序
        stmt = stmt.order_by(
            self.model.path.asc(),  # type: ignore[attr-defined]
            self.model.sort_order.asc()  # type: ignore[attr-defined]
        )

        # 执行查询
        result = await session.execute(stmt)
        return result.scalars().all()

    async def move_node(
        self,
        session: AuditAsyncSession,
        node_id: int,
        new_parent_id: int | None
    ) -> TreeModel:
        """移动节点"""
        node = await self.get_by_id(session, node_id)
        if not node:
            raise errors.RequestError(data={"节点不存在"})

        if new_parent_id:
            if await self._check_cycle(session, node, new_parent_id):
                raise errors.RequestError(data={"不能将节点移动到其子节点下"})

            new_parent = await self.get_by_id(session, new_parent_id)
            if not new_parent:
                raise errors.RequestError(data={"目标父节点不存在"})

            await self._update_node_path(session, node, new_parent)
        else:
            await self._update_node_path(session, node)

        await self._update_children_path(session, node)

        session.add(node)
        await session.flush()

        return node

    async def _clear_tree_cache(self, session: AuditAsyncSession, node: TreeModel) -> None:
        """清除树形结构缓存"""
        # 清除当前节点的缓存
        await redis_client.delete_prefix(
            f"{settings.REDIS_CACHE_KEY_PREFIX}:{self.model.__name__}:tree:"
            f"node:{node.id}"  # type: ignore[attr-defined]
        )

        # 清除父节点的缓存
        if node.parent_id:
            await redis_client.delete_prefix(
                f"{settings.REDIS_CACHE_KEY_PREFIX}:{self.model.__name__}:tree:"
                f"node:{node.parent_id}"
            )

        # 清除根节点缓存
        await redis_client.delete_prefix(
            f"{settings.REDIS_CACHE_KEY_PREFIX}:{self.model.__name__}:tree:"
            f"root"
        )

        # 清除祖先节点缓存
        ancestors = await node.get_ancestors(session)
        for ancestor in ancestors:
            await redis_client.delete_prefix(
                f"{settings.REDIS_CACHE_KEY_PREFIX}:{self.model.__name__}:tree:"
                f"node:{ancestor.id}"  # type: ignore[attr-defined]
            )

    async def validate_node(
        self,
        session: AuditAsyncSession,
        node: TreeModel,
        parent: TreeModel | None = None
    ) -> None:
        """验证节点"""
        # 检查层级深度
        if parent and parent.level >= settings.MAX_TREE_DEPTH:  # type: ignore[attr-defined]
            raise errors.RequestError(data={"超出最大层级深度限制"})

        # 检查同级节点名称唯一性
        if hasattr(node, 'name'):
            siblings = await node.get_siblings(session)
            if any(s.name == node.name and s.id != node.id for s in siblings):  # type: ignore[attr-defined]
                raise errors.RequestError(data={"同级节点名称重复"})

    async def get_siblings(
        self,
        session: AuditAsyncSession,
        node_id: int,
        include_self: bool = False
    ) -> Sequence[TreeModel]:
        """获取同级节点"""
        node = await self.get_by_id(session, node_id)
        if not node:
            raise errors.RequestError(data={"节点不存在"})
        return await node.get_siblings(session, include_self=include_self)

    async def get_ancestors(
        self,
        session: AuditAsyncSession,
        node_id: int,
        include_self: bool = False
    ) -> Sequence[dict]:
        """获取祖先节点"""
        node = await self.get_by_id(session, node_id)
        if not node:
            raise errors.RequestError(data={"节点不存在"})
        ancestors = await node.get_ancestors(session, include_self=include_self)
        return await self.to_tree_dict(ancestors)

    async def bulk_move_nodes(
        self,
        session: AuditAsyncSession,
        node_ids: Sequence[int],
        new_parent_id: int | None
    ) -> Sequence[TreeModel]:
        """批量移动节点"""
        results = []
        for node_id in node_ids:
            try:
                node = await self.move_node(session, node_id, new_parent_id)
                results.append(node)
            except Exception as e:
                # 记录错误但继续处理
                print(f"移动节点 {node_id} 失败: {str(e)}")
        return results

    async def copy_subtree(
        self,
        session: AuditAsyncSession,
        node_id: int,
        new_parent_id: int | None
    ) -> TreeModel:
        """复制子树"""
        # 获取源节点及其子节点
        source_node = await self.get_by_id(session, node_id)
        if not source_node:
            raise errors.RequestError(data={"源节点不存在"})

        # 复制节点数据(排除id和路径相关字段)
        node_data = source_node.model_dump(
            exclude={'id', 'parent_id', 'path', 'level'}
        )
        node_data['parent_id'] = new_parent_id

        # 创建新节点
        new_node = await self.create(session, obj_in=node_data)

        # 递归复制子节点
        children = await source_node.get_children(session)
        for child in children:
            await self.copy_subtree(session, child.id, new_node.id)  # type: ignore[attr-defined]

        return new_node