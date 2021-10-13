import datetime
from functools import total_ordering
from textwrap import shorten
from aiohttp import web
from aiohttp.web_exceptions import HTTPBadRequest
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func, inspect
from sqlalchemy.orm.strategy_options import subqueryload
from sqlalchemy.sql.expression import cast
from sqlalchemy.sql.functions import GenericFunction, user
from sqlalchemy.sql.sqltypes import DateTime, String
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import selectinload
from sqlalchemy.dialects.postgresql import aggregate_order_by
from app.models import sql_engine
from app.models.role import Role
from app.models.user import User
from app.models.phone import Phone
from app.repositories import user_repo
from app.schemas.user_schema import UserSchema


async def delete_user(request: web.Request) -> web.Response:
    async_session = sessionmaker(
        sql_engine, expire_on_commit=False, class_=AsyncSession
    )
    id = int(request.match_info['id'])
    data = {}
    user_schema = UserSchema()
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(User).filter_by(id=id))
            user = result.scalars().first()
            if user is None:
                raise web.HTTPNotFound()
            
            data = user_schema.dump(user)
            await session.delete(user)
            await session.flush()
            await session.commit()

    return web.json_response({
        "success": True,
        "data": data,        
    })

import json

async def update_user(request: web.Request) -> web.Response:
    async_session = sessionmaker(
        sql_engine, expire_on_commit=False, class_=AsyncSession
    )
    try:
        body = await request.json()    
    except:
        raise HTTPBadRequest("Invalid input json")
    
    if "name" not in body:
        raise web.HTTPBadRequest("No field name")
    name = body["name"]

    additional_info = ""
    if "additionalInfo" in body:
        additional_info = body["additionalInfo"]

    roles_id_list = []
    if "roles" in body:
        for role_data in body["roles"]:
            if "id" not in role_data:
                continue
            roles_id_list.append(role_data["id"])

    id = int(request.match_info['id'])

    user_schema = UserSchema()
    data = {}
    async with async_session() as session:
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
            user = result.scalars().one()
            if user is None:
                raise web.HTTPNotFound()
            user.name = name
            user.additional_info = additional_info
            
            result = await session.execute(select(Role).filter(Role.id.in_(roles_id_list)))
            roles = result.scalars()

            user.roles.clear()
            for role in roles:
                user.roles.append(role)

            if "phones" in body:
                new_phones_id_list = [phone_data['id'] for phone_data in body["phones"] if 'id' in phone_data]
                list_phones_difference = [phone for phone in user.phones if phone.id not in new_phones_id_list]
                [(user.phones.remove(phone)) for phone in list_phones_difference]
                
                for phone_data in body["phones"]:
                    phone = None
                    if "id" in phone_data:
                        phone = next((phone for phone in user.phones if phone.id == int(phone_data["id"])), None)
                    if phone is None:
                        phone = Phone()
                        phone.user_id = user.id
                        session.add(phone)
                        user.phones.append(phone)

                    phone.phone = phone_data["phone"]

                pass

            else:
                pass

            await session.flush()
            data = user_schema.dump(user)
            await session.commit()

    return web.json_response({
        "success": True,
        "data": data,        
    })



async def insert_user(request: web.Request) -> web.Response:
    async_session = sessionmaker(
        sql_engine, expire_on_commit=False, class_=AsyncSession
    )
    body = await request.json()    
    if "name" not in body:
        raise web.HTTPBadRequest("No field name")

    
    user = User()
    user.name = str(body["name"])
    
    repo = UserRepository()
    await repo.persist(user)

    schema = UserSchema()
    data = schema.dump(user)

    return web.json_response({
        "success": True,
        "data": data
    })

from app.repositories.user_repo import UserRepository


async def get_user(request: web.Request) -> web.Response: 
    id = int(request.match_info['id'])
    
    repo = UserRepository()
    user = await repo.find(id)
    
    schema = UserSchema()
    
    return web.json_response({
        "data": schema.dump(user)
    })


async def get_users(request: web.Request) -> web.Response:
    page = 1
    if "page" in request.rel_url.query:
        page = int(request.rel_url.query["page"])
    limit = 10
    if "limit" in request.rel_url.query:
        limit = int(request.rel_url.query["limit"])
    offset = (page - 1) * limit

    repo = UserRepository()
    total = await repo.count()
    data = []
    [data.append(record) async for record in repo.stream()]
    
    return web.json_response({
        "success": True,
        "data": data,
        "total": total,
    })

async def get_users_old(request : web.Request):
    page = 1
    if "page" in request.rel_url.query:
        page = int(request.rel_url.query["page"])
    limit = 10
    if "limit" in request.rel_url.query:
        limit = int(request.rel_url.query["limit"])
    offset = (page - 1) * limit

    async_session = sessionmaker(
        sql_engine, expire_on_commit=False, class_=AsyncSession
    )

        # data = await repo.get_list(offset=offset, limit=limit)
        # print(data)
        # async with sql_engine.connect() as conn:
        #     count_select = select(func.count(User.id)).select_from(User)
        #     cursor = await conn.execute(count_select)
        #     total = int(cursor.scalar())
        #     data_select = (
        #         select(
        #             User.id, 
        #             User.name,
        #             func.to_char(User.created_at, 'DD.MM.YYYY HH:MI::SS').label("createdAt"),
        #             func.coalesce(func.string_agg(Role.name.distinct(), ', '), '').label('roles'),
        #             func.coalesce(func.string_agg(Phone.phone.distinct(), ', '), '').label('phones'),
        #         ).select_from(User)
        #         .outerjoin(Role, User.roles)
        #         .outerjoin(Phone, User.phones)
        #         .order_by(User.id)
        #         .limit(limit)
        #         .offset(offset)
        #         .group_by(User.id)
        #     )
            
        #     data_stream = await conn.stream(data_select)

        # async for row in data_stream:
        #     record = {}
        #     for field_name in row.keys():
        #         record[field_name] = row[field_name]
        #     data.append(record)


    return web.json_response({
        "success": True,
        "total": total,
        "data": data,        
    })


async def get_user_old(request: web.Request) -> web.Response: 
    id = int(request.match_info['id'])
    async_session = sessionmaker(
        sql_engine, expire_on_commit=False, class_=AsyncSession
    )
    user_schema = UserSchema()
    data = {}
    async with async_session() as session:
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
            user = result.scalars().one()
            if user is None:
                raise web.HTTPNotFound()
            dump = user_schema.dump(user)
            data = dump
            await session.commit()




    return web.json_response({
        "data": data
    })