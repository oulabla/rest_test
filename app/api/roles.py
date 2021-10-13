from functools import total_ordering
from aiohttp import web
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func, inspect
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.orm.exc import NoResultFound
from app import schemas
from app.models import sql_engine
from app.models.role import Role
from app.schemas.role_schema import RoleSchema
from app.repositories.role_repo import RoleRepository

async def delete_role(request: web.Request) -> web.Response:
    id = int(request.match_info['id'])

    repo = RoleRepository()
    role = await repo.find(id)
    
    schema = RoleSchema()
    data = schema.dump(role)

    await repo.delete(role)

    return web.json_response({
        "success": True,
        "data": data,        
    })


async def update_role(request: web.Request) -> web.Response:
    async_session = sessionmaker(
        sql_engine, expire_on_commit=False, class_=AsyncSession
    )
    body = await request.json()    
    if "name" not in body:
        raise web.HTTPBadRequest("No field name")
    name = body["name"]

    id = int(request.match_info['id'])

    schema = RoleSchema()
    data = {}
    try:
        async with async_session() as session:
            async with session.begin():
                result = await session.execute(select(Role).filter_by(id=id))
                role = result.scalars().first()
                if role is None:
                    raise web.HTTPNotFound()
                role.name = name
                await session.flush()
                data = schema.dump(role)
                await session.commit()
    except Exception as e:
        raise web.HTTPInternalServerError(reason=str(e))

    return web.json_response({
        "success": True,
        "data": data,        
    })



async def insert_role(request: web.Request) -> web.Response:
    body = await request.json()    
    if "name" not in body:
        raise web.HTTPBadRequest("No field name")

    
    role = Role()
    role.name = str(body["name"])

    repo = RoleRepository()
    await repo.persist(role)
    
    schema = RoleSchema()
    data = schema.dump(role)

    return web.json_response({
        "success": True,
        "data": data
    })


async def get_role(request: web.Request) -> web.Response: 
    id = int(request.match_info['id'])
    
   
    repo = RoleRepository()
    role = repo.find(id)
    
    schema = RoleSchema()
    data = schema.dump(role)

    return web.json_response({
        "data": data
    })

async def get_roles(request : web.Request):
    page = 1
    if "page" in request.rel_url.query:
        page = int(request.rel_url.query["page"])
    limit = 10
    if "limit" in request.rel_url.query:
        limit = int(request.rel_url.query["limit"])
    offset = (page - 1) * limit

    repo = RoleRepository()
    total = await repo.count()
    data = []
    [data.append(record) async for record in repo.stream(limit=limit, offset=offset)]

    return web.json_response({
        "success": True,
        "total": total,
        "data": data,        
    })