import jwt
from config import SECRET_JWT_KEY

async def create_jwt_token(user_id: str) -> str:
    payload = {"user_id": user_id}
    token = jwt.encode(payload, SECRET_JWT_KEY, algorithm="HS256")
    return token