import asyncio
from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import create_engine, text, insert
from config import settings
from models import VideokardsORM, Base
import json


sync_engine = create_engine(url=settings.database_url_psycopg,
                       echo=True,
                       # pool_size=5,
                       # max_overflow=10
                       )

async_engine = create_async_engine(url=settings.database_url_asyncpg,
                       echo=True,
                       # pool_size=5,
                       # max_overflow=10
                        )

# with sync_engine.connect() as conn:
#     res = conn.execute(text("SELECT VERSION()"))
#     print(res.first())
#
#
# async def get_async_engine():
#     async with async_engine.connect() as conn:
#         res = await conn.execute(text("SELECT VERSION()"))
#         print(res.first())

# asyncio.run(get_async_engine())

session_factory = sessionmaker(sync_engine)

def create_tables():
    sync_engine.echo = False
    Base.metadata.drop_all(sync_engine)
    Base.metadata.create_all(sync_engine)
    sync_engine.echo = True

# def insert_data(data):
#     values = []
#     for videokard in data.values():
#         values.append({"code": int(videokard['code']),
#                        "guid": videokard['guid'],
#                        "name": videokard['name'],
#                        "description": videokard['description'],
#                        "price": float(videokard['price']),
#                        "imageUrl": videokard['imageUrl'],
#                        "characteristics": json.dumps(videokard['characteristics'], ensure_ascii=False)})
#     with sync_engine.connect() as conn:
#         stmt = insert(videocards).values(values)
#         conn.execute(stmt)
#         conn.commit()

def insert_data(data):
    values = []
    for result in [elem.values() for elem in data]:
        for videokard in result:
            new_videokard = VideokardsORM(code=int(videokard['data']['code']),
                                          guid=videokard['data']['guid'],
                                          name=videokard['data']['name'],
                                          description=videokard['data']['description'],
                                          price=float(videokard['data']['price']),
                                          imageUrl=videokard['data']['imageUrl'],
                                          characteristics=json.dumps(videokard['data']['characteristics'], ensure_ascii=False)
                                      )
            values.append(new_videokard)
    with session_factory() as session:
        session.add_all(values)
        session.commit()

