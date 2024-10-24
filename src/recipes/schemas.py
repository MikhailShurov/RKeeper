from uuid import UUID
from enum import Enum

from pydantic import BaseModel


class RecipeID(BaseModel):
    recipe_id: UUID


class Cuisine(Enum):
    ASIAN = "asian"
    RUSSIAN = "russian"


class Recipe(BaseModel):
    cuisine: Cuisine
    title: str
    ingredients: list[int]
    step_by_step: str
    full_time: int
    photo: str
    published: bool
