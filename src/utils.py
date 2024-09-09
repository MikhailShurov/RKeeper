import hashlib

import jwt
from config import SECRET_JWT_KEY

from src.config import DB_USER, DB_PASS, DB_HOST, DB_NAME, DB_PORT
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from src.db_manager import DBManager

DATABASE_URL = f"postgresql+asyncpg://{DB_NAME}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_USER}?async_fallback=True"

engine = create_async_engine(DATABASE_URL,
                             connect_args={
                                 "ssl": False
                             })
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)  # NOQA


async def get_async_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session


async def get_db_manager() -> DBManager:
    async with async_session_maker() as session:
        return DBManager(session)


async def create_jwt_token(user_id: str) -> str:
    payload = {"user_id": user_id}
    token = jwt.encode(payload, SECRET_JWT_KEY, algorithm="HS256")
    return token


async def decode_jwt_token(token: str) -> dict:
    payload = jwt.decode(token, SECRET_JWT_KEY, algorithms=["HS256"])
    return payload


async def hash_password(password: str) -> str:
    password_bytes = password.encode('utf-8')
    hashed_password = hashlib.sha256(password_bytes).hexdigest()
    return hashed_password