from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect

from fastapi.security import OAuth2PasswordBearer

from src.recipes.schemas import Recipe, RecipeID, Comment
from src.utils import decode_jwt_token, get_mongo_db_manager
from src.utils import opened_websoket_connections
from fastapi.responses import HTMLResponse  # NOQA
# from src.utils import html_template
import uuid

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


@router.get("/get_all")
async def get_recipes(token: str = Depends(oauth2_scheme)):
    token_payload = await decode_jwt_token(token)
    user_id = token_payload["user_id"]
    db_manager_mongo = await get_mongo_db_manager()
    recipes = await db_manager_mongo.user_get_recipes(user_id)
    return recipes


@router.post("/add")
async def add_recipe(recipe: Recipe, token: str = Depends(oauth2_scheme)):
    token_payload = await decode_jwt_token(token)
    user_id = token_payload["user_id"]
    db_manager_mongo = await get_mongo_db_manager()
    await db_manager_mongo.user_add_recipe(user_id, recipe)
    return {"status": "recipe successfully added"}


@router.post("/delete")
async def delete_recipe(recipe_id: RecipeID, token: str = Depends(oauth2_scheme)):
    token_payload = await decode_jwt_token(token)
    recipe_id = str(recipe_id.model_dump()["recipe_id"])
    user_id = token_payload["user_id"]
    db_manager_mongo = await get_mongo_db_manager()
    await db_manager_mongo.user_delete_recipe(user_id, recipe_id)
    return {"status": "recipe successfully deleted"}


@router.post("/update")
async def update_recipe(recipe_id: RecipeID, recipe: Recipe, token: str = Depends(oauth2_scheme)):
    token_payload = await decode_jwt_token(token)
    recipe_id = str(recipe_id.model_dump()["recipe_id"])

    user_id = token_payload["user_id"]
    db_manager_mongo = await get_mongo_db_manager()

    if not await db_manager_mongo.check_if_recipe_exists(user_id, recipe_id):
        raise HTTPException(status_code=404, detail="Recipe not found")

    await db_manager_mongo.user_update_recipe(user_id, recipe_id, recipe)

    return {"message": "Recipe successfully updated"}


@router.get("/get_published")
async def get_recipe(token: str = Depends(oauth2_scheme)):
    token_payload = await decode_jwt_token(token)
    user_id = token_payload["user_id"]
    db_manager_mongo = await get_mongo_db_manager()
    result = await db_manager_mongo.get_published(user_id)
    return result


@router.post("/publish")
async def get_recipe(recipe_id: RecipeID, token: str = Depends(oauth2_scheme)):
    token_payload = await decode_jwt_token(token)
    user_id = token_payload["user_id"]
    db_manager_mongo = await get_mongo_db_manager()
    await db_manager_mongo.publish_recipe(user_id, str(recipe_id.recipe_id))
    return {"message": "Recipe successfully published"}


@router.post("/unpublish")
async def get_recipe(recipe_id: RecipeID, token: str = Depends(oauth2_scheme)):
    token_payload = await decode_jwt_token(token)
    user_id = token_payload["user_id"]
    db_manager_mongo = await get_mongo_db_manager()
    await db_manager_mongo.unpublish_recipe(user_id, str(recipe_id.recipe_id))
    return {"message": "Recipe successfully unpublished"}


@router.get("/get_recipe/{recipe_id}")
async def get_recipe(recipe_id: str, token: str = Depends(oauth2_scheme)):
    token_payload = await decode_jwt_token(token)
    user_id = token_payload["user_id"]
    db_manager_mongo = await get_mongo_db_manager()

    result = await db_manager_mongo.user_get_recipe(user_id, recipe_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Recipe not found")

    return result
    # return HTMLResponse(html_template(recipe_id))


@router.websocket("/ws/djnavjdfvjkdfvjcboerg73bcv83b/{recipe_id}")
async def open_websocket(websocket: WebSocket, recipe_id: str, token: str = Depends(oauth2_scheme)):
    token_payload = await decode_jwt_token(token)
    user_id = token_payload["user_id"]
    db_manager_mongo = await get_mongo_db_manager()
    recipe = await db_manager_mongo.user_get_recipe(user_id, recipe_id)

    if recipe.get('published', False) is False:
        raise HTTPException(status_code=404, detail="Unable to establish websocket connection")

    await websocket.accept()

    if recipe_id not in opened_websoket_connections:
        opened_websoket_connections[recipe_id] = []
    opened_websoket_connections[recipe_id].append(websocket)

    try:
        while True:
            data = await websocket.receive_text()

            comment = Comment(
                comment_id=str(uuid.uuid4()),
                user_id=user_id,
                content=data
            )

            await db_manager_mongo.save_comment(recipe_id, comment)

            for client in opened_websoket_connections[recipe_id]:
                if client != websocket:
                    await client.send_text(data)
    except WebSocketDisconnect:

        opened_websoket_connections[recipe_id].remove(websocket)
        if not opened_websoket_connections[recipe_id]:
            del opened_websoket_connections[recipe_id]
