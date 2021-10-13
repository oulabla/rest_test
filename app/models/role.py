import datetime
from sqlalchemy import Column, String, Integer, DateTime

from . import Base

class Role(Base):
    __tablename__ = 'roles'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)    
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def __str__(self) -> str:
        return f'Role(id: {self.id}, name: {self.name}, created_at: {self.created_at.strftime("%d.%m.%Y %H:%M:%S")})'