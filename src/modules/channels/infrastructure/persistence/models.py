from sqlalchemy import Column, String, JSON, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class ChannelModel(Base):
    __tablename__ = "channels"

    id = Column(String, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    language = Column(String, nullable=False)
    country_code = Column(String, nullable=False)
    urls = Column(JSON, nullable=False)

Base = declarative_base()


class CountryModel(Base):
    __tablename__ = "countries"

    country_code = Column(String, primary_key=True, nullable=False)
    country_name = Column(String, nullable=False)
    timezone = Column(String, nullable=False)
    has_channels = Column(Boolean, nullable=False)
    channel_count = Column(Integer, nullable=False)