import asyncio
from typing import AsyncGenerator
from aiohttp import web
from aiohttp_swagger import *
from concurrent.futures import ThreadPoolExecutor
from urllib.request import urlopen
import random
import time
import aiohttp
import asyncpg
import datetime

from sqlalchemy.sql.functions import mode
from app.utils import DataBase
import uvloop
from app.models import sql_engine
from app.models.user import User
from app.models import sql_engine

from .containers import ApplicationContainer

from app.api.users import get_users, get_user, insert_user, update_user, delete_user
from app.api.roles import get_roles, get_role, insert_role, update_role, delete_role

from app.middlewares import api_exception_json, api_underscore_body



db = DataBase()

def download_content():
    file = urlopen("http://127.0.0.1:8000/text")
    content = file.read()
    return content.decode('utf-8')

async def load_content():
    loop = asyncio.get_running_loop()
    future = loop.run_in_executor(ThreadPoolExecutor(), download_content)
    downloaded_content = await future
    return downloaded_content

async def fetch_external_content():
    async with aiohttp.ClientSession() as session:
        async with session.get("http://127.0.0.1:8000/text") as response:
            print(f'Status: {response.status}')
            html = await response.text()
    return html

async def index_action(request):
    loop = asyncio.get_running_loop()
    # async with Database
    res = await asyncio.gather(load_content(), fetch_external_content())
    content = f'res 1:{res[0]} res 2:{res[1]}'
    # print(res)
    return web.Response(text=content)

async def text_action(request):
    # await asyncio.sleep(2)
    rnd = random.randint(1, 100)
    return web.Response(text=str(rnd))



async def init_database(app :web.Application) -> AsyncGenerator[None, None]:
    app['sql_engine'] = sql_engine
    yield
    await sql_engine.dispose()

container = ApplicationContainer()
container.config.from_yaml('config.yaml')

app: web.Application = container.app()
app.container = container 

app = web.Application(middlewares=[
    api_underscore_body,
    api_exception_json
])

app.cleanup_ctx.extend([
    init_database
])

app.router.add_get('/api/users', get_users)
app.router.add_get('/api/users/{id}', get_user)
app.router.add_post('/api/users', insert_user)
app.router.add_put('/api/users/{id}', update_user)
app.router.add_delete('/api/users/{id}', delete_user)

app.router.add_get('/api/roles', get_roles)
app.router.add_get('/api/roles/{id}', get_role)
app.router.add_post('/api/roles', insert_role)
app.router.add_put('/api/roles/{id}', update_role)
app.router.add_delete('/api/roles/{id}', delete_role)


app.router.add_get('/', index_action)
app.router.add_get('/text', text_action)

app.router.add_get('/di', container.di_view.as_view())

uvloop.install()
setup_swagger(app, swagger_url="/api/v1/doc", ui_version=3)

if __name__ == '__main__':
    print("__MAIN__")
    web.run_app(app, port="8000")

