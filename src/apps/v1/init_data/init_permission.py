from typing import List

from src.apps.v1.sys.models.permission import PermissionCreate
from src.apps.v1.sys.service.permission import svr_permission
from src.common.enums import PermissionType
from src.database.db_session import AuditAsyncSession


async def init_permissions(session: AuditAsyncSession) -> List[PermissionCreate]:
    """初始化权限数据"""
    # 系统管理
    sys_manage = PermissionCreate(
        name="System Management",
        type=PermissionType.MENU,
        code="sys_manage",
        description="System management menu",
        api_path="/system",
        component="Layout",
        icon="setting",
        sort_order=1,
    )
    sys_manage = await svr_permission.create(session, sys_manage)

    # 用户管理相关权限
    user_manage = PermissionCreate(
        name="User Management",
        type=PermissionType.MENU,
        code="user_manage",
        description="User management menu",
        api_path="/system/user",
        component="system/user/index",
        icon="user",
        sort_order=1,
        parent_id=sys_manage.id
    )
    user_manage = await svr_permission.create(session, user_manage)

    user_list = PermissionCreate(
        name="User List",
        type=PermissionType.API,
        code="user_list",
        description="View user list",
        api_path="/api/v1/users",
        api_method="GET",
        parent_id=user_manage.id
    )
    await svr_permission.create(session, user_list)

    user_create = PermissionCreate(
        name="Create User",
        type=PermissionType.API,
        code="user_create",
        description="Create new user",
        api_path="/api/v1/users",
        api_method="POST",
        parent_id=user_manage.id
    )
    await svr_permission.create(session, user_create)

    user_update = PermissionCreate(
        name="Update User",
        type=PermissionType.API,
        code="user_update",
        description="Update user info",
        api_path="/api/v1/users/{id}",
        api_method="PUT",
        parent_id=user_manage.id
    )
    await svr_permission.create(session, user_update)

    user_delete = PermissionCreate(
        name="Delete User",
        type=PermissionType.API,
        code="user_delete",
        description="Delete user",
        api_path="/api/v1/users/{id}",
        api_method="DELETE",
        parent_id=user_manage.id
    )
    await svr_permission.create(session, user_delete)

    # 角色管理相关权限
    role_manage = PermissionCreate(
        name="Role Management",
        type=PermissionType.MENU,
        code="role_manage",
        description="Role management menu",
        api_path="/system/role",
        component="system/role/index",
        icon="peoples",
        sort_order=2,
        parent_id=sys_manage.id
    )
    role_manage = await svr_permission.create(session, role_manage)

    role_list = PermissionCreate(
        name="Role List",
        type=PermissionType.API,
        code="role_list",
        description="View role list",
        api_path="/api/v1/roles",
        api_method="GET",
        parent_id=role_manage.id
    )
    await svr_permission.create(session, role_list)

    role_create = PermissionCreate(
        name="Create Role",
        type=PermissionType.API,
        code="role_create",
        description="Create new role",
        api_path="/api/v1/roles",
        api_method="POST",
        parent_id=role_manage.id
    )
    await svr_permission.create(session, role_create)

    role_update = PermissionCreate(
        name="Update Role",
        type=PermissionType.API,
        code="role_update",
        description="Update role info",
        api_path="/api/v1/roles/{id}",
        api_method="PUT",
        parent_id=role_manage.id
    )
    await svr_permission.create(session, role_update)

    role_delete = PermissionCreate(
        name="Delete Role",
        type=PermissionType.API,
        code="role_delete",
        description="Delete role",
        api_path="/api/v1/roles/{id}",
        api_method="DELETE",
        parent_id=role_manage.id
    )
    await svr_permission.create(session, role_delete)

    # 权限管理相关权限
    perm_manage = PermissionCreate(
        name="Permission Management",
        type=PermissionType.MENU,
        code="permission_manage",
        description="Permission management menu",
        api_path="/system/permission",
        component="system/permission/index",
        icon="lock",
        sort_order=3,
        parent_id=sys_manage.id
    )
    perm_manage = await svr_permission.create(session, perm_manage)

    perm_list = PermissionCreate(
        name="Permission List",
        type=PermissionType.API,
        code="permission_list",
        description="View permission list",
        api_path="/api/v1/permissions",
        api_method="GET",
        parent_id=perm_manage.id
    )
    await svr_permission.create(session, perm_list)

    perm_create = PermissionCreate(
        name="Create Permission",
        type=PermissionType.API,
        code="permission_create",
        description="Create new permission",
        api_path="/api/v1/permissions",
        api_method="POST",
        parent_id=perm_manage.id
    )
    await svr_permission.create(session, perm_create)

    perm_update = PermissionCreate(
        name="Update Permission",
        type=PermissionType.API,
        code="permission_update",
        description="Update permission info",
        api_path="/api/v1/permissions/{id}",
        api_method="PUT",
        parent_id=perm_manage.id
    )
    await svr_permission.create(session, perm_update)

    perm_delete = PermissionCreate(
        name="Delete Permission",
        type=PermissionType.API,
        code="permission_delete",
        description="Delete permission",
        api_path="/api/v1/permissions/{id}",
        api_method="DELETE",
        parent_id=perm_manage.id
    )
    await svr_permission.create(session, perm_delete)

    # 系统设置相关权限
    sys_settings = PermissionCreate(
        name="System Settings",
        type=PermissionType.MENU,
        code="system_settings",
        description="System settings menu",
        api_path="/system/settings",
        component="system/settings/index",
        icon="tool",
        sort_order=4,
        parent_id=sys_manage.id
    )
    sys_settings = await svr_permission.create(session, sys_settings)

    settings_view = PermissionCreate(
        name="View Settings",
        type=PermissionType.API,
        code="settings_view",
        description="View system settings",
        api_path="/api/v1/settings",
        api_method="GET",
        parent_id=sys_settings.id
    )
    await svr_permission.create(session, settings_view)

    settings_update = PermissionCreate(
        name="Update Settings",
        type=PermissionType.API,
        code="settings_update",
        description="Update system settings",
        api_path="/api/v1/settings",
        api_method="PUT",
        parent_id=sys_settings.id
    )
    await svr_permission.create(session, settings_update)

    # 日志管理相关权限
    log_manage = PermissionCreate(
        name="Log Management",
        type=PermissionType.MENU,
        code="log_manage",
        description="Log management menu",
        api_path="/system/log",
        component="system/log/index",
        icon="documentation",
        sort_order=5,
        parent_id=sys_manage.id
    )
    log_manage = await svr_permission.create(session, log_manage)

    log_view = PermissionCreate(
        name="View Logs",
        type=PermissionType.API,
        code="log_view",
        description="View system logs",
        api_path="/api/v1/logs",
        api_method="GET",
        parent_id=log_manage.id
    )
    await svr_permission.create(session, log_view)

    # 仪表盘
    dashboard = PermissionCreate(
        name="Dashboard",
        type=PermissionType.MENU,
        code="dashboard",
        description="System dashboard",
        api_path="/dashboard",
        component="dashboard/index",
        icon="dashboard",
        sort_order=0
    )
    dashboard = await svr_permission.create(session, dashboard)

    dashboard_view = PermissionCreate(
        name="View Dashboard",
        type=PermissionType.API,
        code="dashboard_view",
        description="View dashboard data",
        api_path="/api/v1/dashboard",
        api_method="GET",
        parent_id=dashboard.id
    )
    await svr_permission.create(session, dashboard_view)

    return [
        sys_manage, user_manage, role_manage, perm_manage,
        sys_settings, log_manage, dashboard
    ]
