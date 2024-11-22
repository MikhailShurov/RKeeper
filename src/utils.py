import hashlib
import logging
from typing import List, Dict

import jwt
from fastapi import HTTPException
from fastapi import WebSocket
from pymongo import MongoClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from celery import Celery

from src.config import DB_USER, DB_PASS, DB_HOST, DB_NAME, DB_PORT
from src.config import MONGO_USER, MONGO_PASS, MONGO_HOST, MONGO_PORT, MONGO_DB_NAME
from src.config import SECRET_JWT_KEY
from src.db_manager_mongo import DBManagerMongo
from src.db_manager_postgres import DBManagerPostgres

DATABASE_URL = f"postgresql+asyncpg://{DB_NAME}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_USER}?async_fallback=True"

engine = create_async_engine(DATABASE_URL,
                             connect_args={
                                 "ssl": False
                             })
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)  # NOQA

opened_websoket_connections: Dict[str, List[WebSocket]] = {}

app = Celery('src.celery_tasks.tasks', broker='amqp://guest:guest@rabbitmq//')


async def get_async_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session


async def get_db_manager() -> DBManagerPostgres:
    async with async_session_maker() as session:
        return DBManagerPostgres(session)


logging.basicConfig(level=logging.INFO)

MONGO_URL = f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}/mongodb"
connection = MongoClient(MONGO_URL, authSource="admin")


async def get_mongo_db_manager() -> DBManagerMongo:
    return DBManagerMongo(connection.get_database(MONGO_DB_NAME))


async def create_jwt_token(user_id: str) -> str:
    payload = {"user_id": user_id}
    token = jwt.encode(payload, SECRET_JWT_KEY, algorithm="HS256")
    return token


async def decode_jwt_token(token: str) -> dict:
    payload = jwt.decode(token, SECRET_JWT_KEY, algorithms=["HS256"])
    if payload.get("type", None) is not None:
        raise HTTPException(status_code=400, detail="Invalid jwt token")
    return payload


async def create_tmp_token(user_id: str, secret_code: int, token_exp_timestamp: int) -> str:
    payload = {
        "type": "tmp",
        "user_id": user_id,
        "secret_code": secret_code,
        "token_exp_timestamp": token_exp_timestamp
    }
    token = jwt.encode(payload, SECRET_JWT_KEY, algorithm="HS256")
    return token


async def validate_tmp_token(token: str) -> dict:
    payload = jwt.decode(token, SECRET_JWT_KEY, algorithms=["HS256"])
    if payload.get("type", None) != "tmp":
        raise HTTPException(status_code=400, detail="Invalid jwt token")
    return payload


async def hash_password(password: str) -> str:
    password_bytes = password.encode('utf-8')
    hashed_password = hashlib.sha256(password_bytes).hexdigest()
    return hashed_password


async def verify_password(password: str, hashed_password: str) -> bool:
    return await hash_password(password) == hashed_password


def generate_secret_code():
    from random import randint
    a = randint(0, 10000)
    print(a)
    return a


def check_string_format(input_string):
    tre = input_string.split("@")
    first_word = tre[0]
    if (len(tre) != 2 or len(first_word) > 64 or len(first_word) == 0 or first_word[0] in [".", "_", "-"]
            or first_word[-1] == "."):
        return False

    tr = first_word.split(".")

    for i in tr:
        if len(i) == 0:
            return False

    we = tre[1].split(".")
    if len(tre) != 2 or not we[0].isalpha() or not we[1].isalpha():
        return False

    return True


def html_template(recipe_id: str) -> str:
    return f"""
    <!DOCTYPE html>
    <html>
        <head>
            <title>WebSocket Recipe Chat</title>
            <script>
                const recipeId = "{recipe_id}";
                var ws = new WebSocket(`ws://localhost:8080/recipes/ws/djnavjdfvjkdfvjcboerg73bcv83b/{recipe_id}`);

                ws.onmessage = function(event) {{
                    var messages = document.getElementById('messages');
                    messages.innerHTML += '<div>' + event.data + '</div>';
                }};

                function sendMessage() {{
                    var input = document.getElementById('messageInput');
                    var message = input.value;

                    // Отображаем отправленное сообщение у отправителя
                    var messages = document.getElementById('messages');
                    messages.innerHTML += '<div><strong>Me:</strong> ' + message + '</div>';

                    ws.send(message);
                    input.value = '';
                }}
            </script>
        </head>
        <body>
            <h1>WebSocket Chat for Recipe {recipe_id}</h1>
            <div id="messages" style="border: 1px solid #ccc; height: 300px; overflow-y: scroll;"></div>
            <input id="messageInput" type="text" placeholder="Type a comment...">
            <button onclick="sendMessage()">Send</button>
        </body>
    </html>
    """