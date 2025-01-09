from collections import defaultdict
from typing import Any, AsyncGenerator, Callable, Dict, Generic, List, Sequence, TypeVar

import sqlalchemy as sa

from sqlmodel import SQLModel, insert, select

from src.common.base_model import DatabaseModel
from src.common.enums import HookTypeEnum
from src.common.query_fields import QueryOptions, SortOrder
from src.core.exceptions import errors
from src.database.db_session import AuditAsyncSession

ModelType = TypeVar("ModelType", bound=DatabaseModel)
CreateModelType = TypeVar("CreateModelType", bound=SQLModel)
UpdateModelType = TypeVar("UpdateModelType", bound=SQLModel)

HookType = Callable[..., Any]


class CRUDBase(Generic[ModelType, CreateModelType, UpdateModelType]):
    """基础 CRUD 类"""
    def __init__(self, model: type[ModelType], create_model: type[CreateModelType], update_model: type[UpdateModelType]):
        self.model = model
        self.create_model = create_model
        self.update_model = update_model
        # 初始化钩子字典
        self._hooks: Dict[str, List[HookType]] = defaultdict(list)

    def add_hook(self, hook_type: HookTypeEnum, hook_func: HookType) -> None:
        """添加钩子函数

        Args:
            hook_type: 钩子类型,如 'before_create', 'after_update' 等
            hook_func: 钩子函数
        """
        self._hooks[hook_type].append(hook_func)

    async def _run_hooks(self, hook_type: HookTypeEnum, *args, **kwargs) -> None:
        """运行指定类型的所有钩子函数"""
        for hook in self._hooks[hook_type]:
            await hook(*args, **kwargs)

    async def get_by_id(self, session: AuditAsyncSession, id: Any) -> ModelType | None:
        """获取单个对象"""
        statement = select(self.model).filter_by(id=id)
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    async def get_by_fields(self, session: AuditAsyncSession, **kwargs) -> Sequence[ModelType]:
        """根据字段获取单个对象"""
        statement = select(self.model).filter_by(**kwargs)
        result = await session.execute(statement)
        return result.scalars().all()

    async def get_multi(
        self,
        session: AuditAsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Dict | None = None
    ) -> Sequence[ModelType]:
        """获取列表对象"""
        statement = select(self.model)
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    statement = statement.where(getattr(self.model, field) == value)
        statement = statement.offset(skip).limit(limit)
        result = await session.execute(statement)
        return result.scalars().all()

    async def create(self, session: AuditAsyncSession, *, obj_in: Dict | CreateModelType) -> ModelType:
        """创建对象"""
        if isinstance(obj_in, dict):
            create_data = obj_in
        else:
            create_data = obj_in.model_dump()

        # 运行创建前钩子
        await self._run_hooks(HookTypeEnum.before_create, session, create_data)

        db_obj = self.model(**create_data)
        session.add(db_obj)
        await session.flush()

        # 运行创建后钩子
        await self._run_hooks(HookTypeEnum.after_create, session, db_obj)

        return db_obj

    async def update(
        self,
        session: AuditAsyncSession,
        *,
        obj_in: Dict | UpdateModelType
    ) -> ModelType:
        """更新对象"""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        db_obj = await self.get_by_id(session=session, id=update_data['id'])
        if db_obj is None:
            raise errors.RequestError(data="请求更新的对象不存在！")

        # 运行更新前钩子
        await self._run_hooks(HookTypeEnum.before_update, session, db_obj, update_data)

        for field in update_data:
            if hasattr(db_obj, field):
                setattr(db_obj, field, update_data[field])

        session.add(db_obj)
        await session.flush()

        # 运行更新后钩子
        await self._run_hooks(HookTypeEnum.after_update, session, db_obj)

        return db_obj

    async def delete(self, session: AuditAsyncSession, id: int) -> None:
        """删除对象"""
        obj = await self.get_by_id(session=session, id=id)
        if obj is None:
            raise errors.RequestError(data="请求删除的对象不存在！")

        # 运行删除前钩子
        await self._run_hooks(HookTypeEnum.before_delete, session, obj)

        await session.delete(obj)
        await session.flush()

        # 运行删除后钩子
        await self._run_hooks(HookTypeEnum.after_delete, session, obj)

    async def delete_by_fields(self, session: AuditAsyncSession, **kwargs) -> bool:
        """根据字段删除对象"""
        statement = select(self.model).filter_by(**kwargs)
        result = await session.execute(statement)
        obj = result.scalars().all()
        if not obj:
            raise errors.RequestError(data="请求删除的对象不存在！")
        try:
            await session.delete(obj)
            await session.flush()
        except Exception as e:
            raise errors.RequestError(data=f"删除失败: {e}") from e
        else:
            return True

    async def bulk_create(
        self,
        session: AuditAsyncSession,
        objects: Sequence[Dict | CreateModelType],
        *,
        batch_size: int = 1000,
    ) -> Sequence[ModelType]:
        """批量创建对象

        Args:
            session: 数据库会话
            objects: 要创建的对象列表,可以是字典或模型实例
            batch_size: 每批处理的数据量,默认1000

        Returns:
            创建的对象列表

        Example:
            ```python
            objects = [{"name": "test1"}, {"name": "test2"}]
            # 或
            objects = [Model(name="test1"), Model(name="test2")]

            result = await crud.bulk_create(session, objects)
            ```
        """
        if not objects:
            return []

        # 将所有对象转换为字典
        values = []
        for obj in objects:
            if isinstance(obj, dict):
                values.append(obj)
            else:
                values.append(obj.model_dump())

        created_objects = []

        cols = [getattr(self.model, 'id')] if hasattr(self.model, 'id') else []
        if hasattr(self.model, 'name'):
            cols.append(getattr(self.model, 'name'))
        if hasattr(self.model, 'code'):
            cols.append(getattr(self.model, 'code'))

        tuple_cols = tuple(set(cols))  # 最后转换为tuple

        # 分批处理
        for i in range(0, len(values), batch_size):
            batch = values[i:i + batch_size]

            # 使用insert().values()进行批量插入
            if tuple_cols:
                stmt = insert(self.model).values(batch).returning(*tuple_cols)
            else:
                stmt = insert(self.model).values(batch)
            result = await session.execute(stmt)

            created_objects.extend(result.all())

        await session.flush()
        return created_objects

    async def bulk_create_iterator(
        self,
        session: AuditAsyncSession,
        objects: Sequence[Dict | ModelType],
        *,
        batch_size: int = 1000,
    ) -> AsyncGenerator[Sequence[ModelType], None]:
        """批量创建对象(迭代器版本)

        与bulk_create类似,但会逐批返回创建的对象,适用于数据量较大的场景

        Args:
            session: 数据库会话
            objects: 要创建的对象列表
            batch_size: 每批处理的数据量,默认1000

        Yields:
            每批创建的对象列表

        Example:
            ```python
            objects = [{"name": f"test{i}"} for i in range(10000)]
            async for batch in crud.bulk_create_iterator(session, objects):
                print(f"Created batch of {len(batch)} objects")
            ```
        """
        if not objects:
            return

        values = []
        for obj in objects:
            if isinstance(obj, dict):
                values.append(obj)
            else:
                values.append(obj.model_dump())

        for i in range(0, len(values), batch_size):
            batch = values[i:i + batch_size]
            stmt = insert(self.model).values(batch)
            result = await session.execute(stmt)

            if result.is_insert:
                ids = result.inserted_primary_key_rows
                if ids:
                    stmt = select(self.model).where(
                        getattr(self.model, 'id').in_([id_[0] for id_ in ids])
                    )
                    result = await session.execute(stmt)
                    created_batch = list(result.scalars().all())
                    await session.flush()
                    yield created_batch

    async def bulk_delete(self, session: AuditAsyncSession, ids: Sequence[int]) -> list[int]:
        """批量删除对象

        Args:
            session: 数据库会话
            ids: 要删除的对象ID列表

        Returns:
            删除失败的对象ID列表
        """
        if not ids:
            return []

        # 查询所有存在的对象
        statement = select(self.model).where(getattr(self.model, 'id').in_(ids))
        result = await session.execute(statement)
        existing_objects = result.scalars().all()

        # 找出不存在的ID
        existing_ids = {getattr(obj, 'id') for obj in existing_objects}
        failed_ids = [id_ for id_ in ids if id_ not in existing_ids]

        # 删除存在的对象
        for obj in existing_objects:
            try:
                await session.delete(obj)
            except Exception:
                failed_ids.append(getattr(obj, 'id'))

        await session.flush()
        return failed_ids

    async def get_by_options(
        self,
        session: AuditAsyncSession,
        options: QueryOptions,
    ) -> tuple[int, Sequence[ModelType]]:
        """根据查询选项获取对象列表和总数

        Args:
            session: 数据库会话
            options: 查询选项,包含过滤条件、排序、分页等

        Returns:
            (total, items) 元组,包含总数和对象列表
        """
        # 构建基础查询
        statement = select(self.model)

        # 添加过滤条件
        if options.filters:
            statement = statement.where(options.filters.build_query(self.model))

        # 添加排序
        if options.sort:
            order_by_clauses = []
            for sort_field in options.sort:
                field = getattr(self.model, sort_field.field)
                if sort_field.order == SortOrder.DESC:
                    field = field.desc()
                order_by_clauses.append(field)
            statement = statement.order_by(*order_by_clauses)
        else:
            if hasattr(self.model, 'sort_order'):
                statement = statement.order_by(getattr(self.model, 'sort_order').asc())
            else:
                statement = statement.order_by(getattr(self.model, 'id').desc())

        # 查询总数
        count_stmt = select(sa.func.count()).select_from(statement.alias())
        total = await session.scalar(count_stmt) or 0

        # 添加分页并获取结果
        statement = statement.offset(options.offset).limit(options.limit)
        result = await session.execute(statement)
        items = result.scalars().all()

        return total, items

