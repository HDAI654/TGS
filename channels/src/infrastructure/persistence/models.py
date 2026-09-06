from uuid import UUID
from sqlalchemy import Boolean, ForeignKey, Integer, JSON, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class CategoryModel(Base):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)


class CountryModel(Base):
    __tablename__ = "countries"
    country_code: Mapped[str] = mapped_column(String(2), primary_key=True)
    country_name: Mapped[str] = mapped_column(String(100), nullable=False)
    timezone: Mapped[str] = mapped_column(String(100), nullable=False)
    has_channels: Mapped[bool] = mapped_column(Boolean, nullable=False)
    channel_count: Mapped[int] = mapped_column(Integer, nullable=False)


class ChannelModel(Base):
    __tablename__ = "channels"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False
    )
    language: Mapped[str] = mapped_column(String(50), nullable=False)
    country_code: Mapped[str] = mapped_column(
        ForeignKey("countries.country_code", ondelete="RESTRICT"), nullable=False
    )
    urls: Mapped[dict] = mapped_column(JSON, nullable=False)

    category: Mapped[CategoryModel] = relationship(lazy="raise")
    country: Mapped[CountryModel] = relationship(lazy="raise")
