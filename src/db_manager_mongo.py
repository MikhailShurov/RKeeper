import uuid

from pymongo.database import Database
from src.recipes.schemas import Recipe


class DBManagerMongo:
    def __init__(self, database: Database):
        self.db = database

    def init_user(self, user_id):
        user = self.db.recipes.find_one({"_id": user_id})
        if user is None:
            self.db.recipes.insert_one({
                "_id": user_id,
                "recipes": []
            })

    async def user_get_recipes(self, user_id: str):
        recipes = self.db.recipes.find({"_id": str(user_id)})
        return list(recipes)

    async def user_get_recipe(self, user_id, recipe_id: str):
        # recipe = self.db.recipes.find_one({"_id": user})
        pass

    async def user_add_recipe(self, user_id: str, recipe: Recipe):
        recipe_dict = recipe.model_dump()
        recipe_dict["recipe_id"] = str(uuid.uuid4())
        recipe_dict['cuisine'] = recipe_dict['cuisine'].value
        self.init_user(user_id)
        self.db.recipes.update_one(
            {"_id": user_id},
            {"$push": {"recipes": recipe_dict}}
        )

    async def user_delete_recipe(self, user_id: str, recipe_id: str):
        self.init_user(user_id)
        self.db.recipes.update_one(
            {"_id": user_id},
            {"$pull": {"recipes": {"recipe_id": recipe_id}}}
        )

    async def user_update_recipe(self, user_id: str, recipe_id: str, recipe: Recipe):
        user = await self.db.recipes.find_one({"_id": user_id})
        recipe_dict = recipe.model_dump()
        recipe_dict["recipe_id"] = next(
            (recipe for recipe in user.get("recipes", []) if recipe.get("_id") == recipe_id), None)
        recipe_dict['cuisine'] = recipe_dict['cuisine'].value

    async def get_published(self):
        pass

    async def publish_recipe(self, recipe_id: str):
        pass

    async def unpublish_recipe(self, recipe_id: str):
        pass

    async def get_user_following_latest(self):
        pass

    async def check_if_recipe_exists(self, user_id: str, recipe_id: str) -> bool:
        user = await self.db.recipes.find_one({"_id": user_id})
        if user is None:
            return False

        for recipe in user.get("recipes", []):
            if recipe.get("_id") == recipe_id:
                return True
        return False
