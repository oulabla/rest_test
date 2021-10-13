import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.functions import GenericFunction

sql_engine = create_async_engine(
    'postgresql+asyncpg://postgres:root@localhost:5432/today', echo=True
)

Base = declarative_base()

