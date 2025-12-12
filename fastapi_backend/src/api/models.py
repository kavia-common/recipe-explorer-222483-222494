from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Boolean,
    ForeignKey,
    Table,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# Association table for many-to-many Recipe <-> Category
recipe_categories = Table(
    "recipe_categories",
    Base.metadata,
    Column("recipe_id", ForeignKey("recipes.id", ondelete="CASCADE"), primary_key=True),
    Column("category_id", ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True),
    UniqueConstraint("recipe_id", "category_id", name="uix_recipe_category"),
)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    favorites = relationship("Favorite", back_populates="user", cascade="all, delete-orphan")

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    slug = Column(String(120), unique=True, index=True, nullable=False)

    recipes = relationship("Recipe", secondary=recipe_categories, back_populates="categories")

class Recipe(Base):
    __tablename__ = "recipes"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    instructions = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)
    ingredients = Column(Text, nullable=True)  # comma-separated or JSON string list
    created_at = Column(DateTime, default=datetime.utcnow)

    categories = relationship("Category", secondary=recipe_categories, back_populates="recipes")
    favorited_by = relationship("Favorite", back_populates="recipe", cascade="all, delete-orphan")

class Favorite(Base):
    __tablename__ = "favorites"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    recipe_id = Column(Integer, ForeignKey("recipes.id", ondelete="CASCADE"), index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="favorites")
    recipe = relationship("Recipe", back_populates="favorited_by")

    __table_args__ = (UniqueConstraint("user_id", "recipe_id", name="uix_user_recipe_fav"),)
