from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class UserModel(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True, nullable=False)
    password = Column(String(60), nullable=False)
    email = Column(String, unique=True, nullable=False)
    registration_date = Column(Date, server_default=func.now())
    advertisement = relationship("AdvertisementModel", lazy="joined")


class TokenModel(Base):

    __tablename__ = "tokens"

    id = Column(UUID, server_default=func.uuid_generate_v4(), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    user = relationship("UserModel", lazy="joined")
    creation_time = Column(DateTime, server_default=func.now())


class AdvertisementModel(Base):

    __tablename__ = "advertisements"

    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    created = Column(DateTime, server_default=func.now())
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
