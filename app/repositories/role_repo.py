from . import Repository
from typing import AsyncIterator
from sqlalchemy.future import select
from sqlalchemy import func
from app.models.role import Role


class RoleRepository(Repository):

    async def stream(self,*filters, limit=10, offset=0)  -> AsyncIterator[Role]:
        async with self.session() as session:
            async with session.begin():
                query= (
                    select(
                        Role.id, 
                        Role.name,
                        func.to_char(Role.created_at, 'DD.MM.YYYY HH:MI::SS').label("createdAt"),
                        func.to_char(Role.updated_at, 'DD.MM.YYYY HH:MI::SS').label("updatedAt"),
                    ).select_from(Role)
                    .filter_by(*filters)
                    .order_by(Role.id)                    
                    .limit(limit)
                    .offset(offset)
                    .group_by(Role.id)
                )
        
                data_stream = await session.stream(query)

                async for row in data_stream:
                    record = {}
                    for field_name in row.keys():
                        record[field_name] = row[field_name]
                    yield record


    async def find(self, id : int) -> Role:
        async with self.session() as session:
            async with session.begin():
                select_query = (
                    select(Role).filter_by(id=id)                
                )
                result = await session.execute(select_query)
                return result.scalars().one()


    async def count(self, *filters) -> int:
        async with self.session() as session:
            async with session.begin():
                select_query = (
                    select(func.count(Role.id))
                ).filter_by(*filters)
                result = await session.execute(select_query)
                return result.scalar()
