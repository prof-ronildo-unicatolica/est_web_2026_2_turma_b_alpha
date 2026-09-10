"""seed de cidades e hoteis de exemplo (1 a 5 estrelas)

Revision ID: 004
Revises: 003
Create Date: 2026-09-10 15:10:00.000000

"""

import uuid
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


CIDADE_FORTALEZA_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")
CIDADE_SOBRAL_ID = uuid.UUID("22222222-2222-2222-2222-222222222222")
CIDADE_JERICOACOARA_ID = uuid.UUID("33333333-3333-3333-3333-333333333333")

HOTEL_1_ESTRELA_ID = uuid.UUID("a1111111-1111-1111-1111-111111111111")
HOTEL_2_ESTRELAS_ID = uuid.UUID("a2222222-2222-2222-2222-222222222222")
HOTEL_3_ESTRELAS_ID = uuid.UUID("a3333333-3333-3333-3333-333333333333")
HOTEL_4_ESTRELAS_ID = uuid.UUID("a4444444-4444-4444-4444-444444444444")
HOTEL_5_ESTRELAS_ID = uuid.UUID("a5555555-5555-5555-5555-555555555555")


def upgrade() -> None:
    cidades_table = sa.table(
        "cidades",
        sa.column("id", sa.UUID()),
        sa.column("nome", sa.String()),
    )
    hoteis_table = sa.table(
        "hoteis",
        sa.column("id", sa.UUID()),
        sa.column("nome", sa.String()),
        sa.column("cidade_id", sa.UUID()),
        sa.column("estrelas", sa.Integer()),
    )

    op.bulk_insert(
        cidades_table,
        [
            {"id": CIDADE_FORTALEZA_ID, "nome": "Fortaleza"},
            {"id": CIDADE_SOBRAL_ID, "nome": "Sobral"},
            {"id": CIDADE_JERICOACOARA_ID, "nome": "Jericoacoara"},
        ],
    )

    op.bulk_insert(
        hoteis_table,
        [
            {"id": HOTEL_1_ESTRELA_ID, "nome": "Pousada Economica Sobral", "cidade_id": CIDADE_SOBRAL_ID, "estrelas": 1},
            {"id": HOTEL_2_ESTRELAS_ID, "nome": "Hotel Beira-Mar", "cidade_id": CIDADE_FORTALEZA_ID, "estrelas": 2},
            {"id": HOTEL_3_ESTRELAS_ID, "nome": "Hotel Iracema", "cidade_id": CIDADE_FORTALEZA_ID, "estrelas": 3},
            {"id": HOTEL_4_ESTRELAS_ID, "nome": "Resort Jericoacoara", "cidade_id": CIDADE_JERICOACOARA_ID, "estrelas": 4},
            {"id": HOTEL_5_ESTRELAS_ID, "nome": "Grand Hotel Jericoacoara", "cidade_id": CIDADE_JERICOACOARA_ID, "estrelas": 5},
        ],
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            "DELETE FROM hoteis WHERE id IN ("
            f"'{HOTEL_1_ESTRELA_ID}', '{HOTEL_2_ESTRELAS_ID}', "
            f"'{HOTEL_3_ESTRELAS_ID}', '{HOTEL_4_ESTRELAS_ID}', "
            f"'{HOTEL_5_ESTRELAS_ID}'"
            ")"
        )
    )
    op.execute(
        sa.text(
            "DELETE FROM cidades WHERE id IN ("
            f"'{CIDADE_FORTALEZA_ID}', '{CIDADE_SOBRAL_ID}', "
            f"'{CIDADE_JERICOACOARA_ID}'"
            ")"
        )
    )