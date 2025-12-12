from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field

# Category Schemas
class CategoryBase(BaseModel):
    name: str = Field(..., description="Human readable category name")
    slug: str = Field(..., description="URL-friendly unique slug")

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int

    class Config:
        from_attributes = True

# Recipe Schemas
class RecipeBase(BaseModel):
    title: str = Field(..., description="Title of the recipe")
    description: Optional[str] = Field(None, description="Short description")
    instructions: Optional[str] = Field(None, description="Full instructions")
    image_url: Optional[str] = Field(None, description="Image URL or path")
    ingredients: Optional[str] = Field(None, description="Comma-separated ingredients")

class RecipeCreate(RecipeBase):
    category_ids: List[int] = Field(default_factory=list, description="List of category IDs")

class Recipe(RecipeBase):
    id: int
    created_at: datetime
    categories: List[Category] = []

    class Config:
        from_attributes = True

# Auth and User Schemas
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class User(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# Favorites
class Favorite(BaseModel):
    id: int
    recipe: Recipe
    created_at: datetime

    class Config:
        from_attributes = True

class FavoriteCreate(BaseModel):
    recipe_id: int = Field(..., description="Recipe to favorite")
