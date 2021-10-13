import datetime
from sqlalchemy import Column, String, Integer, DateTime, Table
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.orm import relationship

from . import Base
from .role import Role
from .phone import Phone

role_assoc_table = Table(
    'users_roles',
    Base.metadata,
    Column('user_id', ForeignKey("users.id"), primary_key=True),
    Column('role_id', ForeignKey("roles.id"), primary_key=True),
)


class User(Base):
    __tablename__ = 'users'
    __mapper_args__ = {
        'eager_defaults': True
    }

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    additional_info = Column(String, default='')
    created_at = Column(DateTime, default=datetime.datetime.utcnow)    
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    roles = relationship("Role", lazy='noload', secondary=role_assoc_table)
    phones = relationship("Phone", lazy='noload', cascade="all, delete-orphan")

    def __str__(self) -> str:
        return f'User(id: {self.id}, name: {self.name}, created_at: {self.created_at.strftime("%d.%m.%Y %H:%M:%S")})'

    def __repr__(self) -> str:
        return f'User(id: {self.id}, name: {self.name}, created_at: {self.created_at.strftime("%d.%m.%Y %H:%M:%S")})'