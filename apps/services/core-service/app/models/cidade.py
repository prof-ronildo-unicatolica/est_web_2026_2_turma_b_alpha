import uuid
from typing import List

from sqlalchemy import ForeignKey,String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.tutorial import Base

class Cidade(Base):
    _tablename_="cidades"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=TRUE, default=uuid.uuid4)
    nome: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    hoteis: Mapped[List["Hotel"]] = relationship(
        back_populates="cidade", cascade="all, delete-orphan"
    )