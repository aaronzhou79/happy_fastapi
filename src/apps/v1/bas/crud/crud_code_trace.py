
import sqlalchemy as sa

from src.apps.v1.bas.models.mdl_code_setting import CodeSetting
from src.apps.v1.bas.models.mdl_code_trace import CodeTrace, CodeTraceCreate, CodeTraceUpdate
from src.common.base_crud import CRUDBase
from src.common.enums import CodeGenerationRule, CodeResetFrequency, DocumentType
from src.database.db_session import AuditAsyncSession
from src.utils.timezone import TimeZone


class CrudCodeTrace(CRUDBase[CodeTrace, CodeTraceCreate, CodeTraceUpdate]):
    """单据编号跟踪CRUD操作"""
    def __init__(self) -> None:
        super().__init__(
            model=CodeTrace,
            create_model=CodeTraceCreate,
            update_model=CodeTraceUpdate,
        )

    async def get_next_code(
        self,
        session: AuditAsyncSession,
        doc_type: DocumentType,
        setting: CodeSetting,
        classify_code: str | None = None
    ) -> str:
        """
        获取下一个序列号。

        根据给定的文档类型和设置，获取下一个序列号。如果没有找到对应的记录，则创建一个新的记录。
        根据设置的重置频率（每日、每月、每年或从不），确定查询条件并更新序列号。

        参数:
        session (AsyncSession): 数据库会话。
        document_type (DocumentType): 文档类型。
        setting (DocumentCodeSetting): 文档代码设置，包含重置频率。

        返回:
        str: 生成的文档编号。
        """
        today = TimeZone.now().today()
        year, month, day = today.year, today.month, today.day

        stmt = sa.select(self.model)
        # 根据重置频率确定查询条件
        if setting.reset_frequency == CodeResetFrequency.DAILY:
            stmt = stmt.where(
                getattr(self.model, "doc_type") == doc_type,
                getattr(self.model, "year") == year,
                getattr(self.model, "month") == month,
                getattr(self.model, "day") == day
            )

        elif setting.reset_frequency == CodeResetFrequency.MONTHLY:
            stmt = stmt.where(
                getattr(self.model, "doc_type") == doc_type,
                getattr(self.model, "year") == year,
                getattr(self.model, "month") == month,
            )
        elif setting.reset_frequency == CodeResetFrequency.YEARLY:
            stmt = stmt.where(
                getattr(self.model, "doc_type") == doc_type,
                getattr(self.model, "year") == year,
            )
        else:  # NEVER
            stmt = stmt.where(
                getattr(self.model, "doc_type") == doc_type
            )

        if classify_code:
            stmt = stmt.where(
                getattr(self.model, "classify_code") == classify_code
            )

        # 使用 SELECT FOR UPDATE 锁定记录
        stmt = stmt.with_for_update()
        result = await session.execute(stmt)
        tracker = result.scalar_one_or_none()

        next_sequence = 1 if not tracker else tracker.current_sequence + 1

        if not tracker:
            # 新建记录时，序列号从1开始
            tracker = self.model(
                doc_type=doc_type,
                year=year,
                month=month,
                day=day,
                current_sequence=next_sequence,
                classify_code=classify_code
            )
            session.add(tracker)
        else:
            # 更新记录时，使用当前序列号，并将其加1保存
            tracker.current_sequence = next_sequence
            tracker.year, tracker.month, tracker.day = year, month, day
            tracker.classify_code = classify_code
            await session.flush()

        # 生成日期字符串
        if setting.date_rule == CodeGenerationRule.YYYY:
            str_date: str = f"{year}"
        elif setting.date_rule == CodeGenerationRule.YYYYMM:
            str_date: str = f"{year}{month:02}"
        elif setting.date_rule == CodeGenerationRule.YYYYMMDD:
            str_date: str = f"{year}{month:02}{day:02}"
        else:   # CodeGenerationRule.NONE OR Other
            str_date: str = ""

        suffix_length = setting.suffix_length or 3

        return f'{setting.prefix}{classify_code or ""}{str_date}{str(next_sequence).zfill(suffix_length)}'

    async def confirm_sequence(
        self,
        session: AuditAsyncSession,
        doc_type: DocumentType,
        sequence: int,
        classify_code: str | None = None
    ) -> None:
        """确认并更新序列号"""
        today = TimeZone.now().today()
        year, month, day = today.year, today.month, today.day

        stmt = sa.select(self.model).where(
                getattr(self.model, "doc_type") == doc_type,
                getattr(self.model, "year") == year,
                getattr(self.model, "month") == month,
                getattr(self.model, "day") == day
            )

        if classify_code:
            stmt = stmt.where(
                getattr(self.model, "classify_code") == classify_code
            )

        # 使用 SELECT FOR UPDATE 锁定记录
        stmt = stmt.with_for_update()
        result = await session.execute(stmt)
        tracker = result.scalar_one_or_none()

        if not tracker:
            # 新建记录时，序列号从1开始
            current_sequence = 1
            tracker = self.model(
                id=0,
                doc_type=doc_type,
                year=year,
                month=month,
                day=day,
                current_sequence=current_sequence,
                classify_code=classify_code
            )
            session.add(tracker)
        else:
            # 更新记录时，使用当前序列号，并将其加1保存
            tracker.current_sequence = tracker.current_sequence + 1
            tracker.year, tracker.month, tracker.day = year, month, day
            tracker.classify_code = classify_code
            await session.flush()


crud_code_trace = CrudCodeTrace()
