# src/utils/timezone.py
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Date    : 2024/12/30
# @Author  : Aaron Zhou
# @File    : timezone.py
# @Software: Cursor
# @Description: 时区工具

import zoneinfo

from datetime import datetime
from datetime import timezone as datetime_timezone

from src.core.conf import settings


class TimeZone:
    """
    时区工具类
    """
    tz: str = settings.DATETIME_TIMEZONE
    tz_info: zoneinfo.ZoneInfo = zoneinfo.ZoneInfo(tz)

    @classmethod
    def now(cls) -> datetime:
        """
        获取时区时间

        :return:
        """
        return datetime.now(cls.tz_info)

    @classmethod
    def f_datetime(cls, dt: datetime) -> datetime:
        """
        datetime 时间转时区时间

        :param dt:
        :return:
        """
        return dt.astimezone(cls.tz_info)

    @classmethod
    def f_str(cls, date_str: str, format_str: str = settings.DATETIME_FORMAT) -> datetime:
        """
        时间字符串转时区时间

        :param date_str:
        :param format_str:
        :return:
        """
        return datetime.strptime(date_str, format_str).replace(tzinfo=cls.tz_info)

    @staticmethod
    def f_utc(dt: datetime) -> datetime:
        """
        时区时间转 UTC（GMT）时区

        :param dt:
        :return:
        """
        return dt.astimezone(datetime_timezone.utc)
