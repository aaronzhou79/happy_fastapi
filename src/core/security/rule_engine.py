import ipaddress

from datetime import datetime
from typing import Any, Dict, List

from src.apps.v1.sys.crud.permission_rule import crud_permission_rule
from src.apps.v1.sys.models.permission_rule import Rule, RuleCondition
from src.core.conf import settings
from src.core.exceptions import errors
from src.database.db_redis import redis_client
from src.database.db_session import async_session


class RuleEngine:
    """规则执行引擎"""

    @staticmethod
    async def evaluate_condition(condition: RuleCondition, context: Dict[str, Any]) -> bool:
        """
        评估单个条件

        Args:
            condition: 规则条件
            context: 执行上下文
        """
        try:
            if condition.type == "time":
                return RuleEngine._evaluate_time_condition(condition, context)
            if condition.type == "ip":
                return RuleEngine._evaluate_ip_condition(condition, context)
            if condition.type == "data":
                return RuleEngine._evaluate_data_condition(condition, context)
            raise errors.RuleExecutionError(data=f"不支持的条件类型: {condition.type}")  # noqa: TRY301
        except Exception as e:
            raise errors.RuleExecutionError(data=f"条件执行失败: {str(e)}") from e

    @staticmethod
    def _evaluate_time_condition(condition: RuleCondition, context: Dict[str, Any]) -> bool:
        """评估时间条件"""
        current_time = context.get("current_time", datetime.now())
        if condition.operator == "between":
            start_time, end_time = condition.value
            return start_time <= current_time <= end_time
        return False

    @staticmethod
    def _evaluate_ip_condition(condition: RuleCondition, context: Dict[str, Any]) -> bool:
        """评估IP条件"""
        request_ip = ipaddress.ip_address(context.get("ip", "0.0.0.0"))  # noqa: S104
        if condition.operator == "in":
            allowed_networks = [ipaddress.ip_network(net) for net in condition.value]
            return any(request_ip in network for network in allowed_networks)
        return False

    @staticmethod
    def _evaluate_data_condition(condition: RuleCondition, context: Dict[str, Any]) -> bool:
        """评估数据条件"""
        data = context.get("data", {})
        if condition.operator == "eq":
            return data.get(condition.value["field"]) == condition.value["value"]
        if condition.operator == "in":
            return data.get(condition.value["field"]) in condition.value["values"]
        return False

    @staticmethod
    async def evaluate_rule(rule: Rule, context: Dict[str, Any]) -> bool:
        """
        评估规则

        Args:
            rule: 权限规则
            context: 执行上下文
        """
        results = []
        for condition in rule.conditions:
            result = await RuleEngine.evaluate_condition(condition, context)
            results.append(result)

        if rule.logic == "and":
            return all(results)
        if rule.logic == "or":
            return any(results)
        raise errors.RuleExecutionError(data=f"不支持的逻辑操作符: {rule.logic}")

    @staticmethod
    async def get_permission_rules(permission_id: int) -> List[Rule]:
        """
        获取权限规则(优先从缓存获取)

        Args:
            permission_id: 权限ID
        """
        # 尝试从缓存获取
        cache_key = f"{settings.PERMISSION_RULES_REDIS_PREFIX}:{permission_id}"
        cached_rules = await redis_client.get(cache_key)
        if cached_rules:
            return [Rule.model_validate_json(rule) for rule in cached_rules.split("|")]

        # 从数据库获取
        async with async_session() as session:
            rules = await crud_permission_rule.get_by_permission(
                session=session,
                permission_id=permission_id
            )

        # 缓存规则
        if rules:
            rules_str = "|".join(rule.rule.json() for rule in rules)
            await redis_client.setex(
                cache_key,
                settings.PERMISSION_RULES_REDIS_EXPIRE_SECONDS,
                rules_str
            )
            return [rule.rule for rule in rules]

        return []