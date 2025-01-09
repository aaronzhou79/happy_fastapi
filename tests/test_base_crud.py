from datetime import datetime
from typing import Any, AsyncGenerator

import pytest
import pytest_asyncio

from sqlalchemy import ForeignKey, String
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from src.common.base_crud import CRUDBase, CacheKeyBuilder
from src.common.query_fields import FilterCondition, FilterGroup, FilterOperator, QueryOptions, SortField
from src.core.exceptions import errors
from src.database.cache.cache_utils import CacheManager, CacheResult


# 测试模型定义
class Base(DeclarativeBase):
    pass


class Department(Base):
    __tablename__ = "department"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    deleted_at: Mapped[datetime | None] = mapped_column(nullable=True)
    version: Mapped[int] = mapped_column(default=1)
    employees: Mapped[list["Employee"]] = relationship(back_populates="department")


class Employee(Base):
    __tablename__ = "employee"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    department_id: Mapped[int] = mapped_column(ForeignKey("department.id"))
    department: Mapped[Department] = relationship(back_populates="employees")


# 测试数据模型
from pydantic import BaseModel


class DepartmentCreate(BaseModel):
    name: str


class DepartmentUpdate(BaseModel):
    name: str | None = None


class EmployeeCreate(BaseModel):
    name: str
    department_id: int


class EmployeeUpdate(BaseModel):
    name: str | None = None
    department_id: int | None = None


# Fixtures
@pytest_asyncio.fixture
async def engine():
    """创建测试数据库引擎"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def session(engine) -> AsyncGenerator[AsyncSession, None]:
    """创建测试会话"""
    async_session = AsyncSession(engine, expire_on_commit=False)
    yield async_session
    await async_session.close()


@pytest.fixture
def mock_cache():
    """模拟缓存管理器"""
    class MockCacheManager(CacheManager):
        def __init__(self):
            self.cache = {}
            self.prefix = "test"
            self.default_ttl = 3600

        async def get(self, key: str) -> CacheResult:
            return CacheResult(
                success=True,
                value=self.cache.get(key)
            )

        async def set(
            self,
            key: str,
            value: Any,
            ttl: int | None = None
        ) -> CacheResult:
            self.cache[key] = value
            return CacheResult(success=True, value=value)

        async def delete(self, key: str) -> CacheResult:
            if key in self.cache:
                del self.cache[key]
            return CacheResult(success=True)

    return MockCacheManager()


# 测试类
class TestCRUDBase:
    """测试CRUDBase类"""

    @pytest.fixture
    def dept_crud(self, mock_cache):
        """创建部门CRUD实例"""
        crud = CRUDBase[Department, DepartmentCreate, DepartmentUpdate](
            model=Department,
            cache_prefix="dept",
            cache_ttl=3600
        )
        crud.cache = mock_cache
        return crud

    @pytest.fixture
    def emp_crud(self, mock_cache):
        """创建员工CRUD实例"""
        crud = CRUDBase[Employee, EmployeeCreate, EmployeeUpdate](
            model=Employee,
            cache_prefix="emp",
            cache_ttl=3600
        )
        crud.cache = mock_cache
        return crud

    @pytest.mark.asyncio
    async def test_create(self, session, dept_crud):
        """测试创建记录"""
        dept = await dept_crud.create(
            session,
            DepartmentCreate(name="IT")
        )
        assert dept.id is not None
        assert dept.name == "IT"

    @pytest.mark.asyncio
    async def test_update(self, session, dept_crud):
        """测试更新记录"""
        # 创建测试数据
        dept = await dept_crud.create(
            session,
            DepartmentCreate(name="IT")
        )

        # 更新记录
        updated = await dept_crud.update(
            session,
            db_obj=dept,
            obj_in=DepartmentUpdate(name="HR")
        )
        assert updated.name == "HR"

    @pytest.mark.asyncio
    async def test_delete(self, session, dept_crud):
        """测试删除记录"""
        # 创建测试数据
        dept = await dept_crud.create(
            session,
            DepartmentCreate(name="IT")
        )

        # 删除记录
        deleted = await dept_crud.delete(session, id=dept.id)
        assert deleted.id == dept.id

        # 验证删除
        try:
            result = await dept_crud.get(session, id=dept.id)
        except errors.DBError as e:
            assert str(e) == "记录不存在"

        assert result is None

    @pytest.mark.asyncio
    async def test_get_multi(self, session, dept_crud):
        """测试获取多条记录"""
        # 创建测试数据
        depts = [
            await dept_crud.create(session, DepartmentCreate(name=f"Dept{i}"))
            for i in range(5)
        ]

        # 测试基本查询
        items, total = await dept_crud.get_multi(
            session,
            options=QueryOptions(
                offset=0,
                limit=10
            )
        )
        assert len(items) == 5
        assert total == 5

        # 测试过滤
        items, total = await dept_crud.get_multi(
            session,
            options=QueryOptions(
                filters=FilterGroup(
                    conditions=[
                        FilterCondition(
                            field="name",
                            op=FilterOperator.LIKE,
                            value="Dept1"
                        )
                    ]
                ),
                offset=0,
                limit=10
            )
        )
        assert len(items) == 1
        assert items[0].name == "Dept1"

        # 测试排序
        items, total = await dept_crud.get_multi(
            session,
            options=QueryOptions(
                sort=[SortField(field="name", order="desc")],
                offset=0,
                limit=10
            )
        )
        assert items[0].name > items[-1].name

    @pytest.mark.asyncio
    async def test_create_with_relations(self, session, dept_crud, emp_crud):
        """测试创建关联记录"""
        # 创建部门和员工
        dept = await dept_crud.create(
            session,
            DepartmentCreate(name="IT")
        )

        emp = await emp_crud.create(
            session,
            EmployeeCreate(
                name="John",
                department_id=dept.id
            )
        )

        # 验证关联
        assert emp.department_id == dept.id
        loaded_dept = await dept_crud.get(session, id=dept.id, relationships=["employees"])
        assert len(loaded_dept.employees) == 1
        assert loaded_dept.employees[0].name == "John"

    @pytest.mark.asyncio
    async def test_cache(self, session, dept_crud):
        """测试缓存机制"""
        # 创建记录
        dept = await dept_crud.create(
            session,
            DepartmentCreate(name="IT")
        )

        # 从缓存获取
        cached = await dept_crud.get(session, id=dept.id, use_cache=True)
        assert cached.id == dept.id
        assert cached.name == dept.name

        # 更新记录
        updated = await dept_crud.update(
            session,
            db_obj=dept,
            obj_in=DepartmentUpdate(name="HR")
        )

        # 验证缓存已更新
        cached = await dept_crud.get(session, id=dept.id, use_cache=True)
        assert cached.name == "HR"

    @pytest.mark.asyncio
    async def test_hooks(self, session, dept_crud):
        """测试钩子系统"""
        hook_called = False

        async def test_hook(*args, **kwargs):
            nonlocal hook_called
            hook_called = True

        # 添加钩子
        dept_crud.add_hook("before_create", test_hook)

        # 创建记录
        await dept_crud.create(
            session,
            DepartmentCreate(name="IT")
        )

        assert hook_called

    @pytest.mark.asyncio
    async def test_optimistic_lock(self, session, dept_crud):
        """测试乐观锁"""
        # 创建记录
        dept = await dept_crud.create(
            session,
            DepartmentCreate(name="IT")
        )
        original_version = dept.version

        # 更新记录
        updated = await dept_crud.update(
            session,
            db_obj=dept,
            obj_in=DepartmentUpdate(name="HR"),
            version=original_version
        )
        assert updated.version > original_version

        # 测试版本冲突
        with pytest.raises(Exception):
            await dept_crud.update(
                session,
                db_obj=dept,
                obj_in=DepartmentUpdate(name="Finance"),
                version=original_version
            )

    @pytest.mark.asyncio
    async def test_soft_delete(self, session, dept_crud):
        """测试软删除"""
        # 创建记录
        dept = await dept_crud.create(
            session,
            DepartmentCreate(name="IT")
        )

        # 软删除
        deleted = await dept_crud.soft_delete(session, id=dept.id)
        assert deleted.deleted_at is not None

        # 验证查询会过滤已删除记录
        items, total = await dept_crud.get_multi(session)
        assert len(items) == 0

    @pytest.mark.asyncio
    async def test_bulk_operations(self, session, dept_crud):
        """测试批量操作"""
        # 批量创建
        depts = await dept_crud.create_multi(
            session,
            [DepartmentCreate(name=f"Dept{i}") for i in range(5)]
        )
        assert len(depts) == 5

        # 批量更新
        updated = await dept_crud.update_multi(
            session,
            ids=[d.id for d in depts],
            obj_in=DepartmentUpdate(name="Updated")
        )
        assert all(d.name == "Updated" for d in updated)

        # 批量删除
        deleted = await dept_crud.delete_multi(
            session,
            ids=[d.id for d in depts]
        )
        assert len(deleted) == 5

        # 验证删除
        items, total = await dept_crud.get_multi(session)
        assert len(items) == 0