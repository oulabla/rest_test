from aiohttp import web
import argparse 
import asyncio
import asyncpg
from asyncpg.pool import Pool

# // sudo /etc/init.d/postgresql restart
# DSN = 'postgresql://postgres@192.168.0.8:5432'
DSN = 'postgresql://postgres:root@localhost:5432/today'
# DSN_DB = DSN + '/today'


class DataBase:
    def __init__(self) -> None:
        self.pool: Pool = None
        self.listeners = []

    async def connect(self) -> Pool:
        self.pool = await asyncpg.create_pool(DSN)
        print("Connecting")
        return self.pool

    async def disconnect(self):
        if self.pool:
            releases = [
                self.pool.release(conn) for conn in self.listeners
            ]
            await asyncio.gather(*releases)
            await self.pool.close()

    async def __aenter__(self) -> Pool:
        return await self.connect()

    async def __aexit__(self, *exc):
        await self.disconnect()

    async def add_listener(self, channel, callback):
        conn: asyncpg.Connection = await self.pool.acquire()
        await conn.add_listener(channel, callback)
        self.listeners.append(conn)

async def demo(conn: asyncpg.Connection):
    pk = await conn.fetchval("INSERT INTO users(name) VALUES('Valera') RETURNING id")
    print(pk)
    
async def db_test(request : web.Request):
    user_agent = request.headers['User-Agent']
    async with db as conn:
        try:
            pk = await conn.fetchval(f"INSERT INTO users(name) VALUES('{user_agent}') RETURNING id")
            print(pk)
        except Exception as e:
            print(e)
        
    return web.Response(text="db")

async def atest(request):
    async with sql_engine.begin() as conn:
        await conn
    return web.Response(text="lala")
    
