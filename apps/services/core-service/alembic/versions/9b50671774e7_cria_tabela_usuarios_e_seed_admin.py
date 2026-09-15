"""cria tabela usuarios e seed admin

Revision ID: 9b50671774e7
Revises: 004
Create Date: 2026-09-13 19:35:45.092345

"""
import uuid
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '9b50671774e7'
down_revision: Union[str, None] = '004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('usuarios',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('nome', sa.String(length=100), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('senha_hash', sa.String(length=255), nullable=False),
    sa.Column('is_admin', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )

    usuarios_table = sa.table(
        "usuarios",
        sa.column("id", sa.Uuid()),
        sa.column("nome", sa.String()),
        sa.column("email", sa.String()),
        sa.column("senha_hash", sa.String()),
        sa.column("is_admin", sa.Boolean()),
    )

    op.bulk_insert(
        usuarios_table,
        [
            {
                "id": uuid.UUID("44444444-4444-4444-4444-444444444444"),
                "nome": "Administrador",
                "email": "admin@hotel.com",
                "senha_hash": "$2b$12$fxXghATWUnqrhzYTLsE2AuBOWmLxDT3EO//YLuZBLtZTpXTVF.S5K",
                "is_admin": True,
            }
        ],
    )


def downgrade() -> None:
    op.drop_table('usuarios')