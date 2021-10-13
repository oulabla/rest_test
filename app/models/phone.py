
from sys import maxsize
from . import Base
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

class Phone(Base):
    __tablename__ = 'user_phones'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    phone = Column(String(16))
    user = relationship("User", back_populates="phones")

    def __str__(self) -> str:
        return f'Phone(id: {self.id}, name: {self.phone})' 

    def __repr__(self) -> str:
        return f'Phone(id: {self.id}, name: {self.phone})' 