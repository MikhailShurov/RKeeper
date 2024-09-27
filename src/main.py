import uvicorn
from fastapi import FastAPI

from src.auth.routers import router as auth_router
from src.recipes.routers import router as recipes_router

app = FastAPI(title="RKeeper")

app.include_router(auth_router,
                   prefix="/auth",
                   tags=["auth"], )

app.include_router(recipes_router,
                   prefix="/recipes",
                   tags=["recipes"], )

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
