from typing import List, AsyncIterator
import sqlalchemy
from . import Repository
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import func
from app.models.user import User
from app.models.phone import Phone
from app.models.role import Role


class UserRepository(Repository):



    async def stream(self,*filters, limit=10, offset=0) -> AsyncIterator[User]:
        async with self.session() as session:
            async with session.begin():
                query= (
                    select(
                        User.id, 
                        User.name,
                        func.to_char(User.created_at, 'DD.MM.YYYY HH:MI::SS').label("createdAt"),
                        func.coalesce(func.string_agg(Role.name.distinct(), ', '), '').label('roles'),
                        func.coalesce(func.string_agg(Phone.phone.distinct(), ', '), '').label('phones'),
                    ).select_from(User)
                    .outerjoin(Role, User.roles)
                    .outerjoin(Phone, User.phones)
                    .filter_by(*filters)
                    .order_by(User.id)                    
                    .limit(limit)
                    .offset(offset)
                    .group_by(User.id)
                )
        
                data_stream = await session.stream(query)

                async for row in data_stream:
                    record = {}
                    for field_name in row.keys():
                        record[field_name] = row[field_name]
                    yield record


    async def persist(self, user: User):
        async with self.session() as session:
            async with session.begin():
                session.add(user)
                await session.flush()
                await session.commit()


    async def find(self, id : int) -> User:
        async with self.session() as session:
            async with session.begin():
                select_query = (
                    select(User)
                    .options(
                        selectinload(User.roles), 
                        selectinload(User.phones)
                    )
                    .filter_by(id=id)
                )
                result = await session.execute(select_query)
                return result.scalars().one()


    async def count(self, *filters) -> int:
        async with self.session() as session:
            async with session.begin():
                select_query = (
                    select(func.count(User.id))
                ).filter_by(*filters)
                result = await session.execute(select_query)
                return result.scalar()
