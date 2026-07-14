from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base
from src.modules.core.database import Base


class CountryModel(Base):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True, index=True)
    country_code = Column(String(2), unique=True, nullable=False, index=True)
    country_name = Column(String(100), nullable=False, index=True)
    capital = Column(String(100), nullable=False, index=True)
    timezone = Column(String(100), nullable=False, index=True)
    has_channels = Column(Boolean, nullable=False, index=True)
    channel_count = Column(Integer, nullable=False, index=True)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self):
        return f"<Country(country_code='{self.country_code}', country_name='{self.country_name}')>"


class ChannelModel(Base):
    __tablename__ = "channels"

    id = Column(Integer, primary_key=True, index=True)
    public_id = Column(String(36), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)
    language = Column(String(3), nullable=False, index=True)
    country_code = Column(
        ForeignKey("countries.country_code", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    is_geo_blocked = Column(Boolean, nullable=False, index=True)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self):
        return f"<Channel(public_id='{self.public_id}', name='{self.name}')>"


class URLModel(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, index=True)
    public_id = Column(String(36), unique=True, nullable=False, index=True)
    channel_id = Column(
        ForeignKey("channels.public_id", ondelete="CASCADE"), nullable=False, index=True
    )
    url = Column(String(2048), nullable=False, index=True)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (UniqueConstraint("channel_id", "url", name="uq_channel_url"),)

    def __repr__(self):
        return f"<URL(public_id='{self.public_id}', channel_id='{self.channel_id}')>"
