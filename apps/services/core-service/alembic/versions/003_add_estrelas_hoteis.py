"""adiciona coluna estrelas (1 a 5) na tabela hoteis

Revision ID: 003
Revises: 002
Create Date: 2026-09-10 15:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "hoteis",
        sa.Column("estrelas", sa.Integer(), nullable=False, server_default="3"),
    )
    op.create_check_constraint(
        "ck_hoteis_estrelas_range", "hoteis", "estrelas >= 1 AND estrelas <= 5"
    )
    op.alter_column("hoteis", "estrelas", server_default=None)


def downgrade() -> None:
    op.drop_constraint("ck_hoteis_estrelas_range", "hoteis", type_="check")
    op.drop_column("hoteis", "estrelas")