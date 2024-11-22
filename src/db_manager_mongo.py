import uuid

from pymongo.database import Database

from src.recipes.schemas import Recipe, Comment


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
        recipes = list(self.db.recipes.find({"_id": str(user_id)}))
        result = [{
            'recipe_id': recipe['recipe_id'],
            'title': recipe['title'],
            'image_link': recipe['image_link'],
            'description': recipe['description'],
            'cook_time': recipe['cook_time'],
        } for recipe in recipes[0]['recipes']]
        return result

    async def user_get_recipe(self, user_id: str, recipe_id: str):
        user = self.db.recipes.find_one({"_id": user_id})

        if user is None:
            return None

        user_recipes = user.get('recipes', [])

        for recipe in user_recipes:
            if str(recipe['recipe_id']) == recipe_id:
                return recipe
        return None

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
        user = self.db.recipes.find_one({"_id": user_id})

        recipe_dict = recipe.model_dump()

        updated_recipe = next(
            (recipe for recipe in user.get("recipes", []) if recipe.get("recipe_id") == recipe_id), None)

        if updated_recipe:
            updated_recipe.update(recipe_dict)
            updated_recipe['cuisine'] = recipe_dict['cuisine'].value

            self.db.recipes.update_one(
                {"_id": user_id},
                {"$set": {"recipes": user.get("recipes")}}
            )

    async def save_comment(self, recipe_id: str, comment: Comment):
        pass
        # ToDo save comment
        # result = await self.db.recipes.update_one(
        #     {"recipes.recipe_id": recipe_id},
        #     {"$push": {"recipes.$.comments": comment.model_dump()}}
        # )
        # return result.modified_count > 0

    async def get_published(self, user_id):
        recipes = list(self.db.recipes.find({"_id": str(user_id)}))
        result = [{
            'recipe_id': recipe['recipe_id'],
            'title': recipe['title'],
            'image_link': recipe['image_link'],
            'description': recipe['description'],
            'cook_time': recipe['cook_time'],
        } for recipe in recipes[0]['recipes'] if recipe['published'] is True]
        return result

    async def publish_recipe(self, user_id, recipe_id: str):
        user = self.db.recipes.find_one({"_id": str(user_id)})
        if user is None:
            return False
        updated = False
        for recipe in user['recipes']:
            if recipe['recipe_id'] == recipe_id:
                recipe['published'] = True
                updated = True
                break
        if updated:
            self.db.recipes.update_one(
                {"_id": str(user_id)},
                {"$set": {"recipes": user['recipes']}}
            )
            return True
        return False

    async def unpublish_recipe(self, user_id: str, recipe_id: str):
        user = self.db.recipes.find_one({"_id": str(user_id)})
        if user is None:
            return False
        updated = False
        for recipe in user['recipes']:
            if recipe['recipe_id'] == recipe_id:
                recipe['published'] = False
                updated = True
                break
        if updated:
            self.db.recipes.update_one(
                {"_id": str(user_id)},
                {"$set": {"recipes": user['recipes']}}
            )
            return True
        return False

    async def check_if_recipe_exists(self, user_id: str, recipe_id: str) -> bool:
        user = self.db.recipes.find_one({"_id": user_id})
        if user is None:
            return False

        for recipe in user.get("recipes", []):
            if recipe.get("recipe_id") == recipe_id:
                return True
        return False
