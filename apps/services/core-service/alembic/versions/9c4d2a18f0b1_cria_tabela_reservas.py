"""cria tabela reservas

Revision ID: 9c4d2a18f0b1
Revises: 268c1ee78dd1
Create Date: 2026-11-20 16:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9c4d2a18f0b1"
down_revision: Union[str, None] = "268c1ee78dd1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "reservas",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("usuario_id", sa.Uuid(), nullable=False),
        sa.Column("quarto_id", sa.Uuid(), nullable=False),
        sa.Column("check_in", sa.Date(), nullable=False),
        sa.Column("check_out", sa.Date(), nullable=False),
        sa.Column("hospedes_idades", sa.JSON(), nullable=False),
        sa.Column("servicos_adicionais_ids", sa.JSON(), nullable=False),
        sa.Column("early_check_in", sa.Boolean(), nullable=False),
        sa.Column("late_check_out", sa.Boolean(), nullable=False),
        sa.Column("nao_reembolsavel", sa.Boolean(), nullable=False),
        sa.Column("valor_total", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "PENDENTE",
                "CONFIRMADA",
                "REJEITADA",
                "CANCELADA",
                name="status_reserva_enum",
            ),
            nullable=False,
        ),
        sa.Column("motivo_rejeicao", sa.String(length=255), nullable=True),
        sa.Column("criado_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("check_out > check_in", name="ck_reservas_periodo_valido"),
        sa.CheckConstraint(
            "valor_total >= 0",
            name="ck_reservas_valor_total_nao_negativo",
        ),
        sa.ForeignKeyConstraint(["quarto_id"], ["quartos.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_reservas_check_in"), "reservas", ["check_in"], unique=False)
    op.create_index(op.f("ix_reservas_check_out"), "reservas", ["check_out"], unique=False)
    op.create_index(op.f("ix_reservas_quarto_id"), "reservas", ["quarto_id"], unique=False)
    op.create_index(op.f("ix_reservas_status"), "reservas", ["status"], unique=False)
    op.create_index(op.f("ix_reservas_usuario_id"), "reservas", ["usuario_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_reservas_usuario_id"), table_name="reservas")
    op.drop_index(op.f("ix_reservas_status"), table_name="reservas")
    op.drop_index(op.f("ix_reservas_quarto_id"), table_name="reservas")
    op.drop_index(op.f("ix_reservas_check_out"), table_name="reservas")
    op.drop_index(op.f("ix_reservas_check_in"), table_name="reservas")
    op.drop_table("reservas")
    sa.Enum(name="status_reserva_enum").drop(op.get_bind(), checkfirst=True)
