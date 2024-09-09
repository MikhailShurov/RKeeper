from fastapi import APIRouter, Depends, HTTPException
from src.auth.schemas import Token
from src.utils import create_jwt_token, hash_password
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from typing import Annotated
from src.utils import get_db_manager

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")



@router.post("/register")
async def register(form_data: OAuth2PasswordRequestForm = Depends()):
    db_manager = await get_db_manager()
    user = await db_manager.get_user_id(form_data.username)

    if user is not None:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = await hash_password(form_data.password)
    user_id = await db_manager.create_user(email=form_data.username, hashed_password=hashed_password)

    token = await create_jwt_token(user_id)
    return {"message": "User created successfully", "token": token}


@router.post("/login")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    if form_data.username == 'string' and form_data.password == 'string':
        token = await create_jwt_token('test')
        return Token(token=token, token_type='bearer')
    else:
        raise HTTPException(status_code=400, detail="Incorrect username or password")


