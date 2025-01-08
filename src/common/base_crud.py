import json

from hashlib import sha256
from typing import Any, Awaitable, Callable, Generic, Sequence, Type, TypeVar
from uuid import UUID

import sqlalchemy as sa

from pydantic import BaseModel
from sqlalchemy import Select
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.orm.relationships import RelationshipProperty

from src.common.data_model.query_fields import QueryOptions
from src.core.conf import settings
from src.core.exceptions import errors
from src.database.cache.cache_utils import CacheManager
from src.database.db_session import AuditAsyncSession
from src.utils.timezone import TimeZone

ModelType = TypeVar("ModelType", bound=sa.orm.DeclarativeBase)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

T = TypeVar('T')


class CacheKeyBuilder:
    """缓存键生成器"""

    def __init__(self, prefix: str, hash_func: Callable[[str], str] | None = None):
        """
        初始化

        :param prefix: 缓存前缀
        :param hash_func: 哈希函数
        """
        self.prefix = f"{settings.REDIS_CACHE_KEY_PREFIX}:{prefix}"
        self.hash_func = hash_func or self._default_hash

    def _default_hash(self, data: str) -> str:
        """默认哈希函数"""
        return sha256(data.encode()).hexdigest()[:16]

    def _serialize_value(self, value: Any) -> str:
        """序列化值"""
        if isinstance(value, (str, int, float, bool)):
            return str(value)
        return json.dumps(value, sort_keys=True)

    def build(self, **parts: Any) -> str:
        """
        构建缓存键

        :param parts: 键的组成部分
        :return: 缓存键
        """
        # 基础键
        key_parts = [self.prefix]

        # 添加其他部分
        for k, v in sorted(parts.items()):
            if v is not None:
                serialized = self._serialize_value(v)
                # 对长值进行哈希
                if len(serialized) > 32:
                    serialized = self.hash_func(serialized)
                key_parts.append(f"{k}:{serialized}")

        return ":".join(key_parts)


class BaseCRUD(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """基础CRUD类"""

    def __init__(
        self,
        model: Type[ModelType],
        cached: bool = False,
        cache_prefix: str | None = None,
        cache_ttl: int = 3600,
    ):
        """
        初始化

        :param model: SQLAlchemy模型类
        :param cache_prefix: 缓存前缀
        :param cache_ttl: 缓存过期时间(秒)
        """
        self.model = model
        self.cached = cached
        self.cache = CacheManager(prefix=cache_prefix or model.__name__, default_ttl=cache_ttl)
        self.cache_key_builder = CacheKeyBuilder(self.model.__name__)
        self._before_create_hooks: list[Callable] = []
        self._after_create_hooks: list[Callable] = []
        self._before_update_hooks: list[Callable] = []
        self._after_update_hooks: list[Callable] = []
        self._before_delete_hooks: list[Callable] = []
        self._after_delete_hooks: list[Callable] = []

    def add_hook(self, event: str, hook: Callable[..., Awaitable[Any]]) -> None:
        """
        添加钩子函数(带类型检查)

        :param event: 事件名称
        :param hook: 钩子函数
        :raises ValueError: 当事件类型无效或钩子不可调用时
        """
        if event not in ["before_create", "after_create", "before_update",
                        "after_update", "before_delete", "after_delete"]:
            raise ValueError("事件类型无效")
        hook_list = getattr(self, f"_{event}_hooks", [])
        hook_list.append(hook)
        setattr(self, f"_{event}_hooks", hook_list)

    async def _run_hooks(self, event: str, *args: Any, **kwargs: Any) -> None:
        """
        运行钩子函数

        :param event: 事件名称
        :param args: 位置参数
        :param kwargs: 关键字参数
        """
        hook_list = getattr(self, f"_{event}_hooks")
        for hook in hook_list:
            await hook(*args, **kwargs)

    async def _get_from_cache(self, key: str) -> ModelType | None:
        """从缓存获取数据"""
        result = await self.cache.get(key)
        if result.success and result.value:
            return result.value
        return None

    async def _delete_cache(self, key: str) -> None:
        """删除缓存"""
        await self.cache.delete(key)

    async def create(
        self,
        session: AuditAsyncSession,
        obj_in: CreateSchemaType | dict[str, Any],
    ) -> ModelType:
        """创建记录(带缓存和钩子)"""
        # 运行前置钩子
        await self._run_hooks("before_create", session, obj_in)

        try:
            obj_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump()
            db_obj = self.model(**obj_data)
            session.add(db_obj)
            await session.flush()
            await session.refresh(db_obj)
        except Exception as e:
            await session.rollback()
            raise errors.DBError(msg=f"创建记录失败: {str(e)}") from e
        else:
            # 设置缓存
            await self._set_cache(f"id_{db_obj.id}", db_obj)
            # 运行后置钩子
            await self._run_hooks("after_create", session, db_obj)
            return db_obj

    async def update(
        self,
        session: AuditAsyncSession,
        *,
        db_obj: ModelType,
        obj_in: UpdateSchemaType | dict[str, Any],
        version: int | None = None,  # 乐观锁版本号
    ) -> ModelType:
        """更新记录(带乐观锁、缓存和钩子)"""
        # 乐观锁检查
        if version is not None and hasattr(db_obj, 'version'):
            if db_obj.version != version:
                raise errors.DBError(msg="数据已被其他用户修改")

        # 运行前置钩子
        await self._run_hooks("before_update", session, db_obj, obj_in)

        try:
            obj_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)
            for field in obj_data:
                if hasattr(db_obj, field):
                    setattr(db_obj, field, obj_data[field])
            # 更新版本号
            if hasattr(db_obj, 'version'):
                db_obj.version += 1
            await session.flush()
            await session.refresh(db_obj)
        except Exception as e:
            await session.rollback()
            raise errors.DBError(msg=f"更新记录失败: {str(e)}") from e
        else:
            # 更新缓存
            await self._set_cache(f"id_{db_obj.id}", db_obj)
            # 运行后置钩子
            await self._run_hooks("after_update", session, db_obj)
            return db_obj

    async def delete(
        self,
        session: AuditAsyncSession,
        *,
        id: int | str | UUID,
    ) -> ModelType:
        """删除记录(带缓存和钩子)"""
        # 运行前置钩子
        await self._run_hooks("before_delete", session, id)

        try:
            stmt = sa.select(self.model).where(getattr(self.model, "id") == id)
            result = await session.execute(stmt)
            db_obj = result.scalar_one_or_none()

            if db_obj is None:
                raise errors.DBError(msg="记录不存在")
            if hasattr(db_obj, 'deleted_at'):
                if getattr(db_obj, 'deleted_at') is not None:
                    raise errors.DBError(msg="记录已被逻辑删除，不能再次操作删除！")
                setattr(db_obj, 'deleted_at', TimeZone.now())
            else:
                await session.delete(db_obj)

            await session.flush()
            if db_obj:
                # 删除缓存
                await self._delete_cache(f"id_{id}")
                # 运行后置钩子
                await self._run_hooks("after_delete", session, db_obj)
        except Exception as e:
            await session.rollback()
            raise errors.DBError(msg=f"删除记录失败: {str(e)}") from e
        else:
            return db_obj

    async def delete_by_fields(self, session: AuditAsyncSession, /, **kwargs: Any) -> None:
        """通过字段删除记录"""
        try:
            stmt = self._build_select(**kwargs)
            result = await session.execute(stmt)
            db_obj = result.scalars().all()
            for obj in db_obj:
                await session.delete(obj)
                # 删除缓存
                await self._delete_cache(f"id_{obj.id}")
                # 运行后置钩子
                await self._run_hooks("after_delete", session, obj)
            await session.flush()
        except Exception as e:
            raise errors.DBError(msg=f"删除记录失败: {str(e)}") from e

    def _build_select(self, /, **kwargs: Any) -> Select[tuple[ModelType]]:
        """构建条件"""
        stmt = sa.select(self.model)

        # 将kwargs转换为条件表达式
        if kwargs:
            conditions = []
            for key, value in kwargs.items():
                if hasattr(self.model, key):
                    conditions.append(getattr(self.model, key) == value)
            if conditions:
                stmt = stmt.where(*conditions)

        return stmt

    async def get(
        self,
        session: AuditAsyncSession,
        id: int | str | UUID,
        use_cache: bool = True,
        relationships: list[str] | None = None
    ) -> ModelType | None:
        """
        获取单条记录(带缓存)

        :param relationships: 需要加载的关联关系列表
        """
        if use_cache and not relationships:  # 有关联加载时不使用缓存
            cached_obj = await self._get_from_cache(f"id_{id}")
            if cached_obj:
                return cached_obj

        # 构建查询
        stmt = self._build_select(id=id)

        # 添加关联加载
        if relationships:
            for rel in relationships:
                prop = getattr(self.model, rel).property
                if isinstance(prop, RelationshipProperty):
                    # 多对一和一对一使用joinedload
                    if prop.uselist is False:
                        stmt = stmt.options(joinedload(getattr(self.model, rel)))
                    # 一对多和多对多使用selectinload
                    else:
                        stmt = stmt.options(selectinload(getattr(self.model, rel)))

        result = await session.execute(stmt)
        db_obj = result.scalar_one_or_none()

        if db_obj and use_cache and not relationships:
            await self._set_cache(f"id_{id}", db_obj)
        return db_obj.to_dict() if db_obj else None

    async def get_multi_with_lock(
        self,
        session: AuditAsyncSession,
        *,
        options: QueryOptions | None = None,
        relationships: list[str] | None = None,
        for_update: bool = True,
    ) -> tuple[Sequence[ModelType], int]:
        """获取多条记录(带悲观锁)"""
        query = self.get_base_query()

        # 添加悲观锁
        if for_update:
            query = query.with_for_update()

        # 其他查询条件保持不变
        return await self.get_multi_with_relations(
            session,
            options=options,
            relationships=relationships,
            base_query=query
        )

    async def bulk_create(
        self,
        session: AuditAsyncSession,
        objs_in: list[CreateSchemaType] | list[dict[str, Any]],
        chunk_size: int = 1000
    ) -> Sequence[ModelType]:
        """优化的批量创建"""
        all_objs = []
        # 分块处理
        for i in range(0, len(objs_in), chunk_size):
            chunk = objs_in[i:i + chunk_size]
            objs = await self.create_multi(session, chunk)
            all_objs.extend(objs)
        return all_objs

    async def execute_in_transaction(
        self,
        session: AuditAsyncSession,
        callback: Callable[..., Awaitable[T]],
        *args: Any,
        **kwargs: Any
    ) -> T:
        """在事务中执行操作"""
        try:
            result = await callback(*args, **kwargs)
        except Exception as e:
            await session.rollback()
            raise errors.DBError(msg=f"事务执行失败: {str(e)}") from e
        else:
            return result

    def get_base_query(self) -> Select:
        """
        获取基础查询

        :return: SQLAlchemy查询对象
        """
        return sa.select(self.model)

    async def get_multi(
        self,
        session: AuditAsyncSession,
        *,
        options: QueryOptions | None = None,
    ) -> tuple[Sequence[ModelType], int]:
        """
        获取多条记录

        :param session: 数据库会话
        :param options: 查询选项
        :return: (记录列表, 总数)
        """
        options = options or QueryOptions()
        query = self.get_base_query()

        # 添加过滤条件
        if options.filters:
            query = query.where(options.filters.build_query(self.model))

        # 添加排序
        if options.sort:
            query = query.order_by(*(
                getattr(self.model, sort_field.field).desc()
                if sort_field.order.value == "desc"
                else getattr(self.model, sort_field.field).asc()
                for sort_field in options.sort
            ))

        # 执行计数查询
        count_query = sa.select(sa.func.count()).select_from(self.model)
        if options.filters:
            count_query = count_query.where(options.filters.build_query(self.model))
        total = await session.scalar(count_query) or 0

        # 添加分页
        query = query.offset(options.offset).limit(options.limit)

        # 执行查询
        result = await session.scalars(query)
        items = result.all()

        return items, total

    async def create_multi(
        self,
        session: AuditAsyncSession,
        objs_in: list[CreateSchemaType] | list[dict[str, Any]],
    ) -> list[ModelType]:
        """
        批量创建记录(带钩子支持)
        """
        try:
            # 执行前置钩子
            for obj in objs_in:
                await self._run_hooks("before_create", session, obj)

            # 创建记录
            db_objs = [self.model(**obj_data) for obj_data in objs_in]
            session.add_all(db_objs)
            await session.flush()

            # 刷新并执行后置钩子
            for obj in db_objs:
                await session.refresh(obj)
                await self._run_hooks("after_create", session, obj)

        except Exception as e:
            await session.rollback()
            raise errors.DBError(msg=f"批量创建记录失败: {str(e)}") from e
        else:
            return list(db_objs)

    async def update_multi(
        self,
        session: AuditAsyncSession,
        *,
        ids: list[int | str | UUID],
        obj_in: UpdateSchemaType | dict[str, Any]
    ) -> list[ModelType]:
        """
        批量更新记录

        :param session: 数据库会话
        :param ids: ID列表
        :param obj_in: 更新数据
        :return: 更新后的记录列表
        """
        obj_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)

        # 查询所有对象
        query = sa.select(self.model).where(self.model.id.in_(ids))
        result = await session.scalars(query)
        db_objs = result.all()

        # 更新每个对象
        for db_obj in db_objs:
            for field in obj_data:
                if hasattr(db_obj, field):
                    setattr(db_obj, field, obj_data[field])

        await session.flush()

        # 刷新所有对象
        for obj in db_objs:
            await session.refresh(obj)

        return list(db_objs)

    async def delete_multi(
        self,
        session: AuditAsyncSession,
        *,
        ids: list[int | str | UUID],
    ) -> list[ModelType]:
        """
        批量删除记录

        :param session: 数据库会话
        :param ids: ID列表
        :return: 删除的记录列表
        """
        # 查询所有对象
        query = sa.select(self.model).where(self.model.id.in_(ids))
        result = await session.scalars(query)
        db_objs = result.all()

        # 删除所有对象
        for obj in db_objs:
            if hasattr(obj, 'deleted_at'):
                if getattr(obj, 'deleted_at') is not None:
                    raise errors.DBError(msg="记录已被逻辑删除，不能再次操作删除！")
                setattr(obj, 'deleted_at', TimeZone.now())
            else:
                await session.delete(obj)
            # 删除缓存
            await self._delete_cache(f"id_{obj.id}")
            # 运行后置钩子
            await self._run_hooks("after_delete", session, obj)

        await session.flush()
        return list(db_objs)

    async def create_with_relations(
        self,
        session: AuditAsyncSession,
        obj_in: CreateSchemaType | dict[str, Any],
    ) -> ModelType:
        """
        创建记录(包含关联数据)

        :param session: 数据库会话
        :param obj_in: 创建数据
        :return: 创建的记录
        """
        obj_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump()

        # 分离关联数据
        relationship_data = {}
        model_data = {}

        for key, value in obj_data.items():
            if key in self.model.__mapper__.relationships:
                relationship_data[key] = value
            else:
                model_data[key] = value

        # 创建主表记录
        db_obj = self.model(**model_data)
        session.add(db_obj)
        await session.flush()

        # 处理关联数据
        for rel_name, rel_data in relationship_data.items():
            relationship = self.model.__mapper__.relationships[rel_name]
            if relationship.uselist:  # 一对多/多对多
                await self._handle_list_relationship(session, db_obj, rel_name, rel_data)
            else:  # 一对一
                await self._handle_scalar_relationship(session, db_obj, rel_name, rel_data)

        await session.refresh(db_obj)
        return db_obj

    async def _handle_list_relationship(
        self,
        session: AuditAsyncSession,
        db_obj: ModelType,
        rel_name: str,
        rel_data: list[dict[str, Any]],
    ) -> None:
        """处理列表类型的关联关系"""
        relationship = self.model.__mapper__.relationships[rel_name]
        target_model = relationship.mapper.class_

        # 创建关联对象
        related_objs = []
        for item_data in rel_data:
            if isinstance(item_data, dict):
                # 设置外键
                if relationship.direction.name == 'ONETOMANY':
                    local_col = list(relationship.local_columns)[0]
                    item_data[local_col.name] = db_obj.id

                related_obj = target_model(**item_data)
                related_objs.append(related_obj)

        if related_objs:
            session.add_all(related_objs)

            # 处理多对多关系
            if relationship.direction.name == 'MANYTOMANY':
                setattr(db_obj, rel_name, related_objs)

    async def _handle_scalar_relationship(
        self,
        session: AuditAsyncSession,
        db_obj: ModelType,
        rel_name: str,
        rel_data: dict[str, Any],
    ) -> None:
        """处理标量类型的关联关系"""
        if not rel_data:
            return

        relationship = self.model.__mapper__.relationships[rel_name]
        target_model = relationship.mapper.class_

        # 设置外键
        if relationship.direction.name == 'MANYTOONE':
            local_col = list(relationship.local_columns)[0]
            setattr(db_obj, local_col.name, rel_data['id'])
        else:
            related_obj = target_model(**rel_data)
            session.add(related_obj)
            setattr(db_obj, rel_name, related_obj)

    async def update_with_relations(
        self,
        session: AuditAsyncSession,
        *,
        db_obj: ModelType,
        obj_in: UpdateSchemaType | dict[str, Any]
    ) -> ModelType:
        """
        更新记录(包含关联数据)

        :param session: 数据库会话
        :param db_obj: 数据库对象
        :param obj_in: 更新数据
        :return: 更新后的记录
        """
        obj_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)

        # 分离关联数据
        relationship_data = {}
        model_data = {}

        for key, value in obj_data.items():
            if key in self.model.__mapper__.relationships:
                relationship_data[key] = value
            else:
                model_data[key] = value

        # 更新主表数据
        for field in model_data:
            if hasattr(db_obj, field):
                setattr(db_obj, field, model_data[field])

        # 更新关联数据
        for rel_name, rel_data in relationship_data.items():
            relationship = self.model.__mapper__.relationships[rel_name]
            if relationship.uselist:
                await self._update_list_relationship(session, db_obj, rel_name, rel_data)
            else:
                await self._update_scalar_relationship(session, db_obj, rel_name, rel_data)

        await session.flush()
        await session.refresh(db_obj)
        return db_obj

    async def _update_list_relationship(
        self,
        session: AuditAsyncSession,
        db_obj: ModelType,
        rel_name: str,
        rel_data: list[dict[str, Any]],
    ) -> None:
        """更新列表类型的关联关系"""
        relationship = self.model.__mapper__.relationships[rel_name]
        target_model = relationship.mapper.class_

        # 获取现有关联对象
        existing_items = getattr(db_obj, rel_name)
        existing_map = {item.id: item for item in existing_items}

        # 处理更新和新增
        updated_ids = set()
        for item_data in rel_data:
            item_id = item_data.get('id')
            if item_id and item_id in existing_map:
                # 更新现有对象
                item = existing_map[item_id]
                for field, value in item_data.items():
                    if hasattr(item, field):
                        setattr(item, field, value)
                updated_ids.add(item_id)
            else:
                # 创建新对象
                if relationship.direction.name == 'ONETOMANY':
                    local_col = list(relationship.local_columns)[0]
                    item_data[local_col.name] = db_obj.id
                new_item = target_model(**item_data)
                session.add(new_item)
                if relationship.direction.name == 'MANYTOMANY':
                    existing_items.append(new_item)

        # 删除未包含在更新数据中的对象
        for item in list(existing_items):
            if hasattr(item, 'id') and item.id not in updated_ids:
                if relationship.direction.name == 'MANYTOMANY':
                    existing_items.remove(item)
                else:
                    await session.delete(item)

    async def _update_scalar_relationship(
        self,
        session: AuditAsyncSession,
        db_obj: ModelType,
        rel_name: str,
        rel_data: dict[str, Any] | None,
    ) -> None:
        """更新标量类型的关联关系"""
        relationship = self.model.__mapper__.relationships[rel_name]
        target_model = relationship.mapper.class_

        if rel_data is None:
            # 清除关联
            if relationship.direction.name == 'MANYTOONE':
                local_col = list(relationship.local_columns)[0]
                setattr(db_obj, local_col.name, None)
            else:
                setattr(db_obj, rel_name, None)
            return

        existing_item = getattr(db_obj, rel_name)
        if existing_item and 'id' in rel_data and existing_item.id == rel_data['id']:
            # 更新现有对象
            for field, value in rel_data.items():
                if hasattr(existing_item, field):
                    setattr(existing_item, field, value)
        else:
            # 创建新对象或设置关联
            if relationship.direction.name == 'MANYTOONE':
                local_col = list(relationship.local_columns)[0]
                setattr(db_obj, local_col.name, rel_data['id'])
            else:
                new_item = target_model(**rel_data)
                session.add(new_item)
                setattr(db_obj, rel_name, new_item)

    async def soft_delete(
        self,
        session: AuditAsyncSession,
        *,
        id: int | str | UUID,
    ) -> ModelType | None:
        """
        软删除记录

        :param session: 数据库会话
        :param id: 记录ID
        :return: 删除的记录
        """
        stmt = sa.select(self.model).where(getattr(self.model, "id") == id)
        result = await session.execute(stmt)
        db_obj = result.scalar_one_or_none()
        if db_obj and hasattr(db_obj, 'deleted_at'):
            db_obj.deleted_at = TimeZone.now()
            await session.flush()
            await session.refresh(db_obj)
        return db_obj

    async def get_multi_with_relations(
        self,
        session: AuditAsyncSession,
        *,
        options: QueryOptions | None = None,
        relationships: list[str] | None = None,
        base_query: Select | None = None,
    ) -> tuple[Sequence[ModelType], int]:
        """
        获取多条记录(包含关联数据)

        :param session: 数据库会话
        :param options: 查询选项
        :param relationships: 要加载的关联关系
        :return: (记录列表, 总数)
        """
        options = options or QueryOptions()
        query = base_query if base_query is not None else self.get_base_query()

        # 添加关联加载
        if relationships:
            for rel_name in relationships:
                if rel_name in self.model.__mapper__.relationships:
                    query = query.options(selectinload(getattr(self.model, rel_name)))

        # 添加软删除过滤
        if hasattr(self.model, 'deleted_at'):
            query = query.where(self.model.deleted_at.is_(None))

        # 添加查询条件
        if options.filters:
            query = query.where(options.filters.build_query(self.model))

        # 添加排序
        if options.sort:
            query = query.order_by(*(
                getattr(self.model, sort_field.field).desc()
                if sort_field.order.value == "desc"
                else getattr(self.model, sort_field.field).asc()
                for sort_field in options.sort
            ))

        # 执行计数查询
        count_query = sa.select(sa.func.count()).select_from(self.model)
        if hasattr(self.model, 'deleted_at'):
            count_query = count_query.where(self.model.deleted_at.is_(None))
        if options.filters:
            count_query = count_query.where(options.filters.build_query(self.model))
        total = await session.scalar(count_query) or 0

        # 添加分页
        query = query.offset(options.offset).limit(options.limit)

        # 执行查询
        result = await session.scalars(query)
        items = result.all()

        return items, total

    def _generate_query_cache_key(
        self,
        options: QueryOptions | None = None,
        relationships: list[str] | None = None,
        **kwargs: Any
    ) -> str:
        """
        生成查询缓存键

        :param options: 查询选项
        :param relationships: 关联关系
        :param kwargs: 其他参数
        :return: 缓存键
        """
        cache_parts = {}

        # 添加查询选项
        if options:
            if options.filters:
                cache_parts['filters'] = options.filters
            if options.sort:
                cache_parts['sort'] = options.sort
            cache_parts['offset'] = options.offset
            cache_parts['limit'] = options.limit

        # 添加关联关系
        if relationships:
            cache_parts['relations'] = sorted(relationships)

        # 添加其他参数
        cache_parts.update(kwargs)

        return self.cache_key_builder.build(**cache_parts)

    async def get_multi_cached(
        self,
        session: AuditAsyncSession,
        *,
        options: QueryOptions | None = None,
        relationships: list[str] | None = None,
        cache_ttl: int | None = None,
        force_refresh: bool = False,
        **kwargs: Any
    ) -> tuple[Sequence[ModelType], int]:
        """
        获取多条记录(带缓存)

        :param session: 数据库会话
        :param options: 查询选项
        :param relationships: 要加载的关联关系
        :param cache_ttl: 缓存过期时间(秒)
        :param force_refresh: 强制刷新缓存
        :param kwargs: 其他参数
        :return: (记录列表, 总数)
        """
        # 使用自定义或默认的缓存键生成器

        # 生成缓存键
        cache_key = self.cache_key_builder.build(
            options=options,
            relationships=relationships,
            **kwargs
        )

        # 如果不强制刷新,尝试从缓存获取
        if not force_refresh:
            cached_result = await self._get_from_cache(cache_key)
            if cached_result:
                return cached_result

        # 从数据库查询
        result = await self.get_multi_with_relations(
            session,
            options=options,
            relationships=relationships,
            **kwargs
        )

        # 设置缓存
        if cache_ttl != 0:  # 0表示不缓存
            await self._set_cache(
                cache_key,
                result,
                ttl=cache_ttl or self.cache.default_ttl
            )

        return result

    async def _set_cache(
        self,
        key: str,
        value: Any,
        ttl: int | None = None
    ) -> None:
        """
        设置缓存

        :param key: 缓存键
        :param value: 缓存值
        :param ttl: 过期时间(秒)
        """
        if self.cached:
            await self.cache.set(
                key,
                value,
                ttl=ttl or self.cache.default_ttl
            )

    async def invalidate_cache(self, pattern: str | None = None) -> None:
        """
        使缓存失效

        :param pattern: 缓存键模式,为None时清除所有缓存
        """
        if pattern:
            await self.cache.delete(f"{self.cache.prefix}:{pattern}")
        else:
            await self.cache.delete(f"{self.cache.prefix}:*")

    async def get_by_id(
        self,
        session: AuditAsyncSession,
        id: int | str | UUID,
        use_cache: bool = True,
    ) -> ModelType | None:
        """
        通过ID获取单条记录(带缓存)

        Args:
            session: 数据库会话
            id: 记录ID
            use_cache: 是否使用缓存
            relationships: 需要加载的关联关系列表
        """
        if use_cache:
            cached_obj = await self._get_from_cache(f"id_{id}")
            if cached_obj:
                return cached_obj

        # 构建查询
        stmt = sa.select(self.model).where(
            getattr(self.model, "id") == id
        )

        result = await session.execute(stmt)
        db_obj = result.scalar_one_or_none()

        if db_obj and use_cache:
            await self._set_cache(f"id_{id}", db_obj)
        return db_obj

    async def get_by_fields(self, session: AuditAsyncSession, **kwargs: Any) -> ModelType | None:
        """通过字段获取单条记录"""
        stmt = self._build_select(**kwargs)
        result = await session.execute(stmt)
        return result.unique().scalar_one_or_none()

    def by_query(self) -> Select[tuple[ModelType]]:
        """
        构建基础查询语句,自动加载关联数据并转换外键

        Returns:
            Select查询对象
        """
        # 构建基础查询
        stmt = sa.select(self.model)

        # 获取所有关系
        relationships = self.model.__mapper__.relationships

        # 处理每个关系
        for rel_name, rel in relationships.items():
            # 获取目标模型
            target_model = rel.mapper.class_

            # 检查目标模型是否有name或code字段
            display_field = None
            if hasattr(target_model, 'name'):
                display_field = 'name'
            elif hasattr(target_model, 'code'):
                display_field = 'code'

            if display_field:
                # 构建子查询以获取显示字段
                subquery = (
                    sa.select(
                        target_model.id,
                        getattr(target_model, display_field).label(f"{rel_name}_{display_field}")
                    )
                    .correlate(self.model)
                    .scalar_subquery()
                )

                # 添加到主查询
                stmt = stmt.add_columns(subquery.label(f"{rel_name}_{display_field}"))

            # 根据关系类型选择加载策略
            if rel.uselist is False:
                # 多对一和一对一使用joinedload
                stmt = stmt.options(joinedload(getattr(self.model, rel_name)))
            else:
                # 一对多和多对多使用selectinload
                stmt = stmt.options(selectinload(getattr(self.model, rel_name)))

        return stmt
