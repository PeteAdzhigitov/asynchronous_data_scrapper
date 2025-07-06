import datetime

from sqlalchemy import Table, Integer, Float, String, MetaData, Column, JSON, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from typing import Annotated


str256 =Annotated[str, 256]

class Base(DeclarativeBase):
    type_annotation_map = {

        str256: String(256)
    }


intpk = Annotated[int, mapped_column(primary_key=True)]
created_at = Annotated[datetime.datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]
updated_at = Annotated[datetime.datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"),
                                                        onupdate=datetime.datetime.utcnow)]

class VideokardsORM(Base):

    __tablename__ = "videokards"

    id: Mapped[intpk]
    code: Mapped[int] = mapped_column(unique=True)
    guid: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str256]
    description: Mapped[str]
    price: Mapped[float]
    imageUrl: Mapped[str]
    characteristics: Mapped[dict] = mapped_column(JSONB)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]