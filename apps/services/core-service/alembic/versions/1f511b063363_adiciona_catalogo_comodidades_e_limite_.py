"""adiciona catalogo comodidades e limite territorial

Revision ID: 1f511b063363
Revises: 9b50671774e7
Create Date: 2026-09-20 18:19:15.799209

"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1f511b063363"
down_revision: str | None = "9b50671774e7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "comodidades",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("nome", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("nome"),
    )

    op.create_table(
        "hotel_comodidades",
        sa.Column("hotel_id", sa.Uuid(), nullable=False),
        sa.Column("comodidade_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["comodidade_id"],
            ["comodidades.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["hotel_id"],
            ["hoteis.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("hotel_id", "comodidade_id"),
    )

    op.add_column(
        "cidades",
        sa.Column(
            "limite_territorial",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("cidades", "limite_territorial")
    op.drop_table("hotel_comodidades")
    op.drop_table("comodidades")
