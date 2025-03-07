#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Description: 数据库迁移脚本

import argparse
import os
import subprocess  # noqa: S404
import sys

# 将项目根目录添加到sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.conf import settings


def run_command(command):
    """运行命令并打印输出"""
    print(f"执行命令: {command}")
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        encoding="utf-8",
        errors="replace",
    )

    stdout, stderr = process.communicate()

    if stdout:
        print(stdout)

    if stderr:
        print(f"命令执行结果: \r\n{stderr}")

    return process.returncode


def create_migration(message):
    """创建新的迁移脚本"""
    command = f'alembic revision --autogenerate -m "{message}"'
    return run_command(command)


def upgrade(revision="head", checkfirst=False):
    """升级数据库到指定版本

    Args:
        revision: 目标版本，默认为最新版本
        checkfirst: 是否在创建对象前检查是否已存在
    """
    command = f"alembic upgrade {revision}"
    if checkfirst:
        # 设置环境变量，让alembic知道需要检查对象是否存在
        os.environ["ALEMBIC_CHECKFIRST"] = "1"
        print("已启用checkfirst模式，将在创建对象前检查是否已存在")
    return run_command(command)


def downgrade(revision="-1", checkfirst=False):
    """降级数据库到指定版本

    Args:
        revision: 目标版本，默认为上一个版本
        checkfirst: 是否在创建对象前检查是否已存在
    """
    command = f"alembic downgrade {revision}"
    if checkfirst:
        os.environ["ALEMBIC_CHECKFIRST"] = "1"
        print("已启用checkfirst模式，将在创建对象前检查是否已存在")
    return run_command(command)


def show_history():
    """显示迁移历史"""
    command = "alembic history"
    return run_command(command)


def show_current():
    """显示当前版本"""
    command = "alembic current"
    return run_command(command)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="数据库迁移工具")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # 创建迁移
    create_parser = subparsers.add_parser("create", help="创建新的迁移脚本")
    create_parser.add_argument("-m", "--message", required=True, help="迁移说明")

    # 升级数据库
    upgrade_parser = subparsers.add_parser("upgrade", help="升级数据库")
    upgrade_parser.add_argument(
        "-r", "--revision", default="head", help="目标版本，默认为最新版本"
    )
    upgrade_parser.add_argument(
        "--checkfirst", action="store_true", help="在创建对象前检查是否已存在"
    )

    # 降级数据库
    downgrade_parser = subparsers.add_parser("downgrade", help="降级数据库")
    downgrade_parser.add_argument(
        "-r", "--revision", default="-1", help="目标版本，默认为上一个版本"
    )
    downgrade_parser.add_argument(
        "--checkfirst", action="store_true", help="在创建对象前检查是否已存在"
    )

    # 显示历史
    subparsers.add_parser("history", help="显示迁移历史")

    # 显示当前版本
    subparsers.add_parser("current", help="显示当前版本")

    # 初始化数据库
    init_parser = subparsers.add_parser("init", help="初始化数据库")
    init_parser.add_argument(
        "--checkfirst", action="store_true", help="在创建对象前检查是否已存在"
    )

    args = parser.parse_args()

    if args.command == "create":
        return create_migration(args.message)
    elif args.command == "upgrade":
        return upgrade(args.revision, getattr(args, "checkfirst", False))
    elif args.command == "downgrade":
        return downgrade(args.revision, getattr(args, "checkfirst", False))
    elif args.command == "history":
        return show_history()
    elif args.command == "current":
        return show_current()
    elif args.command == "init":
        # 初始化数据库
        print(f"初始化数据库: {settings.DB_NAME}")
        return upgrade(checkfirst=getattr(args, "checkfirst", False))
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
