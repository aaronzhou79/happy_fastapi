# 账套管理

在需要进行账套管理的MODEL中添加TenantMixin
```python
class Demo(DemoBase, TenantMixin, DateTimeMixin, DatabaseModel, table=True):
    """DEMO表"""
    __tablename__: Literal["demo"] = "demo"

    # Relationships
    demo_items: list["DemoItem"] = Relationship(back_populates="demo")
```

需要前端在请求时，携带账套ID
增加请求头：
    X-Tenant-Id: 租户ID
