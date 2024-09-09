from http.client import HTTPException

from fastapi import APIRouter, Depends
from src.auth.schemas import Token
from src.utils import create_jwt_token
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from typing import Annotated

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")



@router.post("/get_all")
async def register(data: OAuth2PasswordRequestForm = Depends(oauth2_scheme)):
    token = await create_jwt_token('2-30i2')
    return {"token": token, "token_type": "bearer"}


@router.post("/login")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    if form_data.username == 'string' and form_data.password == 'string':
        token = await create_jwt_token('test')
        return Token(token=token, token_type='bearer')
    else:
        raise HTTPException(status_code=400, detail="Incorrect username or password")


