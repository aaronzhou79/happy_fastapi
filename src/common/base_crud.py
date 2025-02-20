import inspect

from collections import defaultdict
from dataclasses import dataclass
from typing import Any, AsyncGenerator, Callable, Dict, Generic, Sequence, TypeVar, Union

import sqlalchemy as sa

from sqlmodel import SQLModel, insert, select

from src.common.base_model import CreateModelType, DatabaseModel, ModelType, UpdateModelType
from src.common.enums import HookTypeEnum
from src.common.query_fields import QueryOptions, SortOrder
from src.common.tree_model import TreeModel
from src.core.exceptions import errors
from src.database.db_session import AuditAsyncSession


# 定义钩子上下文类型
@dataclass
class HookContext:
    """钩子执行上下文"""
    session: AuditAsyncSession
    params: Dict[str, Any]
    results: Dict[str, Any]


# 定义钩子函数类型
HookFunc = Callable[[HookContext], Any]


@dataclass
class Hook:
    """钩子配置类"""
    func: HookFunc  # 钩子函数
    priority: int = 0  # 优先级,数字越小优先级越高
    condition: Callable[[HookContext], bool] | None = None  # 执行条件
    error_handler: Callable[[Exception, HookContext], Any] | None = None  # 错误处理器


class HookManager:
    """钩子管理器"""
    def __init__(self):
        self.hooks: Dict[HookTypeEnum, list[Hook]] = defaultdict(list)

    def add_hook(
        self,
        hook_type: HookTypeEnum,
        func: HookFunc,
        priority: int = 0,
        condition: Callable[[HookContext], bool] | None = None,
        error_handler: Callable[[Exception, HookContext], Any] | None = None
    ) -> None:
        """添加钩子"""
        hook = Hook(func=func, priority=priority, condition=condition, error_handler=error_handler)
        self.hooks[hook_type].append(hook)
        # 按优先级排序
        self.hooks[hook_type].sort(key=lambda x: x.priority)

    async def execute_hooks(self, hook_type: HookTypeEnum, context: HookContext) -> None:
        """执行指定类型的钩子"""
        for hook in self.hooks[hook_type]:
            # 检查条件
            if hook.condition and not hook.condition(context):
                continue

            try:
                # 处理同步/异步函数
                if inspect.iscoroutinefunction(hook.func):
                    await hook.func(context)
                else:
                    hook.func(context)
            except Exception as e:
                if hook.error_handler:
                    hook.error_handler(e, context)
                else:
                    raise


class CRUDBase(Generic[ModelType, CreateModelType, UpdateModelType]):
    """基础 CRUD 类"""
    def __init__(self, model: type[ModelType], create_model: type[CreateModelType], update_model: type[UpdateModelType]):
        self.model = model
        self.create_model = create_model
        self.update_model = update_model
        self.hook_manager = HookManager()

    def hook(
        self,
        hook_type: HookTypeEnum,
        priority: int = 0,
        condition: Callable[[HookContext], bool] | None = None,
        error_handler: Callable[[Exception, HookContext], Any] | None = None
    ) -> Callable[[HookFunc], HookFunc]:
        """钩子装饰器"""
        def decorator(func: HookFunc) -> HookFunc:
            self.hook_manager.add_hook(
                hook_type=hook_type,
                func=func,
                priority=priority,
                condition=condition,
                error_handler=error_handler
            )
            return func
        return decorator

    async def _run_hooks(self, hook_type: HookTypeEnum, **kwargs) -> Dict[str, Any]:
        """运行指定类型的钩子"""
        context = HookContext(
            session=kwargs.get('session'),   # type: ignore
            params=kwargs,
            results={}
        )
        await self.hook_manager.execute_hooks(hook_type, context)
        return context.results

    # 创建方法
    async def _create_relation(
        self,
        session: AuditAsyncSession,
        db_obj: ModelType,
        obj_in: Dict | CreateModelType) -> None:
        """创建关联对象"""
        if not hasattr(self.model, '__relation_info__'):
            return

        for _relation, _relation_info in self.model.__relation_info__.items():
            relation_model = _relation_info['relation_model']
            relation_obj = getattr(obj_in, _relation)
            if isinstance(relation_obj, list):
                for item in relation_obj:
                    for _rel_key, _rel_info in relation_model.__foreign_info__.items():
                        if hasattr(item, _rel_key):
                            setattr(item, _rel_key, getattr(db_obj, _rel_info["target_column"]))
                            await relation_model.create(session, obj_in=item)

    async def create(self, session: AuditAsyncSession, *, obj_in: Dict | CreateModelType) -> ModelType:
        """创建对象"""
        try:
            # 运行创建前钩子
            hook_results = await self._run_hooks(
                HookTypeEnum.before_create,
                session=session,
                obj_in=obj_in,
            )

            # 允许钩子修改创建数据
            if 'modified_data' in hook_results:
                obj_in = hook_results['modified_data']

            db_obj = await self.model.create(session, obj_in=obj_in)

            await self._create_relation(session, db_obj, obj_in)

            # 运行创建后钩子
            await self._run_hooks(
                HookTypeEnum.after_create,
                session=session,
                db_obj=db_obj,
                obj_in=obj_in
            )

            await session.flush()
        except Exception as e:
            raise errors.RequestError(data=f"创建失败: {e}") from e
        else:
            return db_obj

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
        if hasattr(self.model, "sort_order"):
            statement = statement.order_by(getattr(self.model, "sort_order").asc())
        else:
            statement = statement.order_by(getattr(self.model, "id").desc())
        statement = statement.offset(skip).limit(limit)
        result = await session.execute(statement)
        return result.scalars().all()

    async def update(self, session: AuditAsyncSession, *, obj_in: Dict | UpdateModelType) -> ModelType:
        """更新对象"""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        db_obj = await self.get_by_id(session=session, id=update_data['id'])
        if db_obj is None:
            raise errors.RequestError(data="请求更新的对象不存在！")

        # 运行更新前钩子
        await self._run_hooks(
            HookTypeEnum.before_update,
            session=session,
            db_obj=db_obj,
            obj_in=obj_in
        )

        for field in update_data:
            if hasattr(db_obj, field):
                setattr(db_obj, field, update_data[field])

        session.add(db_obj)
        await session.flush()

        # 运行更新后钩子
        await self._run_hooks(
            HookTypeEnum.after_update,
            session=session,
            db_obj=db_obj,
            obj_in=obj_in
        )

        return db_obj

    async def delete(self, session: AuditAsyncSession, id: int) -> None:
        """删除对象"""
        obj = await self.get_by_id(session=session, id=id)
        if obj is None:
            raise errors.RequestError(data="请求删除的对象不存在！")

        # 运行删除前钩子
        await self._run_hooks(HookTypeEnum.before_delete, session=session, db_obj=obj)

        await session.delete(obj)
        await session.flush()

        # 运行删除后钩子
        await self._run_hooks(HookTypeEnum.after_delete, session=session, db_obj=obj)

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

    async def has_ids(
        self,
        session: AuditAsyncSession,
        ids: Sequence[int]
    ) -> Sequence[int] | None:
        """根据ID列表判断对象是否存在,并返回不存在的ID列表"""
        statement = select(self.model).where(getattr(self.model, 'id').in_(ids))
        result = await session.execute(statement)
        data = result.scalars().all()
        if not data:
            return ids
        exist_ids = {getattr(obj, 'id') for obj in data}
        # 从ids中移除存在的ID
        return [id_ for id_ in ids if id_ not in exist_ids]

