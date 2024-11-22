from uuid import UUID
from enum import Enum

from pydantic import BaseModel


class RecipeID(BaseModel):
    recipe_id: UUID


class Cuisine(Enum):
    ASIAN = "asian"
    RUSSIAN = "russian"


class Comment(BaseModel):
    comment_id: str
    user_id: str
    content: str


class Recipe(BaseModel):
    cuisine: Cuisine
    title: str
    ingredients: list[int]
    image_link: str
    description: str
    step_by_step: str
    cook_time: int
    photo: str
    published: bool
    comments: list[Comment]
