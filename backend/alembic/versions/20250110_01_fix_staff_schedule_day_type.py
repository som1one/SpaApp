"""Convert staff_schedules.day_of_week enum to integer

Revision ID: 20250110_01
Revises: 60a244a29737
Create Date: 2025-11-22 12:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20250110_01"
down_revision: Union[str, None] = "60a244a29737"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

DAY_ENUM_TO_INT = {
    "MONDAY": 0,
    "TUESDAY": 1,
    "WEDNESDAY": 2,
    "THURSDAY": 3,
    "FRIDAY": 4,
    "SATURDAY": 5,
    "SUNDAY": 6,
}


def _is_integer_column(column_type) -> bool:
    """Проверяет, что колонка уже INTEGER."""
    return isinstance(column_type, sa.Integer)


def _convert_enum_column_to_int() -> None:
    """Выполняет преобразование ENUM -> INTEGER."""
    op.add_column(
        "staff_schedules",
        sa.Column("day_of_week_int", sa.Integer(), nullable=True),
    )

    # Конвертация существующих значений
    conversion_case = " ".join(
        [
            "CASE day_of_week::text",
            *[
                f"WHEN '{name}' THEN {value}"
                for name, value in DAY_ENUM_TO_INT.items()
            ],
            "ELSE NULL",
            "END",
        ]
    )

    op.execute(
        sa.text(
            f"""
            UPDATE staff_schedules
            SET day_of_week_int = {conversion_case}
            """
        )
    )

    # Если вдруг остались NULL (например, из-за нестандартных значений) - ставим понедельник
    op.execute(
        """
        UPDATE staff_schedules
        SET day_of_week_int = 0
        WHERE day_of_week_int IS NULL
        """
    )

    op.drop_column("staff_schedules", "day_of_week")
    op.execute(
        "ALTER TABLE staff_schedules RENAME COLUMN day_of_week_int TO day_of_week"
    )
    op.execute(
        "ALTER TABLE staff_schedules ALTER COLUMN day_of_week SET NOT NULL"
    )
    # Удаляем старый ENUM тип, если он больше не используется
    op.execute("DROP TYPE IF EXISTS dayofweek CASCADE")


def _fix_invalid_time_ranges() -> None:
    """Нормализует интервал рабочего дня."""
    op.execute(
        """
        UPDATE staff_schedules
        SET
            start_time = '09:00:00',
            end_time = '18:00:00',
            break_start = '13:00:00',
            break_end = '14:00:00'
        WHERE
            start_time IS NOT NULL
            AND end_time IS NOT NULL
            AND start_time >= end_time
        """
    )


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    # Если таблицы staff_schedules нет (например, миграция с её созданием
    # не входила в текущую ветку БД) — просто пропускаем изменения.
    existing_tables = inspector.get_table_names()
    if "staff_schedules" not in existing_tables:
        print("⚠️ Таблица staff_schedules не найдена, миграция пропущена")
        return

    columns = {col["name"]: col for col in inspector.get_columns("staff_schedules")}

    day_column = columns.get("day_of_week")
    if not day_column:
        print("⚠️ Колонка staff_schedules.day_of_week не найдена, изменений нет")
        return

    if _is_integer_column(day_column["type"]):
        print("ℹ️ Колонка day_of_week уже INTEGER — пропускаем конвертацию")
    else:
        print("🔧 Конвертируем day_of_week из ENUM в INTEGER")
        _convert_enum_column_to_int()

    _fix_invalid_time_ranges()
    print("✅ Некорректные интервалы времени приведены к 09:00-18:00")


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = {col["name"]: col for col in inspector.get_columns("staff_schedules")}

    day_column = columns.get("day_of_week")
    if not day_column:
        print("⚠️ Колонка staff_schedules.day_of_week отсутствует, откат не требуется")
        return

    if hasattr(day_column["type"], "enums"):
        print("ℹ️ Колонка day_of_week уже ENUM — откат не требуется")
        return

    dayofweek_enum = sa.Enum(
        *DAY_ENUM_TO_INT.keys(),
        name="dayofweek",
    )
    dayofweek_enum.create(conn, checkfirst=True)

    op.add_column(
        "staff_schedules",
        sa.Column("day_of_week_enum", dayofweek_enum, nullable=True),
    )

    conversion_case = " ".join(
        [
            "CASE day_of_week",
            *[
                f"WHEN {value} THEN '{name}'"
                for name, value in DAY_ENUM_TO_INT.items()
            ],
            "ELSE 'MONDAY'",
            "END",
        ]
    )
    op.execute(
        sa.text(
            f"""
            UPDATE staff_schedules
            SET day_of_week_enum = {conversion_case}
            """
        )
    )

    op.drop_column("staff_schedules", "day_of_week")
    op.execute(
        "ALTER TABLE staff_schedules RENAME COLUMN day_of_week_enum TO day_of_week"
    )
    op.execute(
        "ALTER TABLE staff_schedules ALTER COLUMN day_of_week SET NOT NULL"
    )

