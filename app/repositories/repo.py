import abc
from typing import AsyncIterator
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select

from app.models import Base, sql_engine


class Repository(abc.ABC):
    

    def __init__(self, session: AsyncSession=None) -> None:
        if session is None:
                session = sessionmaker(
                sql_engine, expire_on_commit=False, class_=AsyncSession
            )
        self.session = session
        self.enter_session = None

    @abc.abstractmethod
    async def find(self, id : int) -> Base:
        pass

    @abc.abstractmethod
    async def count(self, *filters) -> int:
        pass
    
    @abc.abstractmethod
    async def stream(self, *filters, limit:int=10, offset:int=0)  -> AsyncIterator[Base]:
        pass

    async def delete(self, model: Base):
         async with self.session() as session:
            async with session.begin():
                await session.delete(model)
                await session.flush()
                await session.commit()

    async def persist(self, model: Base):
        async with self.session() as session:
            async with session.begin():
                session.add(model)
                await session.flush()
                await session.commit()

