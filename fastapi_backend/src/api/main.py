import os
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .db import engine, get_db
from .models import Base, Category, Recipe, User
from .routers_auth import router as auth_router
from .routers_categories import router as categories_router
from .routers_recipes import router as recipes_router
from .routers_favorites import router as favorites_router
from .routers_images import router as images_router
from .auth import hash_password

tags_metadata = [
    {"name": "auth", "description": "User signup and login"},
    {"name": "recipes", "description": "Browse and search recipes"},
    {"name": "categories", "description": "Recipe categories"},
    {"name": "favorites", "description": "Manage user favorites"},
    {"name": "images", "description": "Image uploads and serving"},
]

app = FastAPI(
    title="Recipe Explorer API",
    description="API for browsing, searching, and saving recipes with categories and images.",
    version="0.1.0",
    openapi_tags=tags_metadata,
)

# CORS: allow frontend origin or default to wildcard
frontend_url = os.getenv("FRONTEND_URL")
allow_origins: List[str] = [frontend_url] if frontend_url else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router)
app.include_router(categories_router)
app.include_router(recipes_router)
app.include_router(favorites_router)
app.include_router(images_router)

# PUBLIC_INTERFACE
@app.get("/", tags=["health"])
def health_check():
    """Health check endpoint."""
    return {"message": "Healthy"}

def seed_data(db: Session):
    """Create baseline categories, sample user, and a few recipes if empty."""
    # Categories
    default_categories = [
        ("Breakfast", "breakfast"),
        ("Lunch", "lunch"),
        ("Dinner", "dinner"),
        ("Dessert", "dessert"),
        ("Vegan", "vegan"),
    ]
    for name, slug in default_categories:
        if not db.query(Category).filter(Category.slug == slug).first():
            db.add(Category(name=name, slug=slug))
    db.commit()

    # Sample user
    email = "demo@example.com"
    if not db.query(User).filter(User.email == email).first():
        db.add(User(email=email, password_hash=hash_password("password")))
        db.commit()

    # Recipes
    if db.query(Recipe).count() == 0:
        # Attach categories by slug
        def cats(*slugs):
            return [db.query(Category).filter(Category.slug == s).first() for s in slugs]

        r1 = Recipe(
            title="Avocado Toast",
            description="Simple and healthy avocado toast.",
            instructions="Toast bread, mash avocado, season with salt, pepper, and chili flakes.",
            image_url="/images/avocado_toast.jpg",
            ingredients="bread,avocado,salt,pepper,chili flakes,olive oil",
            categories=cats("breakfast", "vegan"),
        )
        r2 = Recipe(
            title="Grilled Chicken Salad",
            description="Protein-packed salad with grilled chicken.",
            instructions="Grill chicken, chop veggies, toss with dressing.",
            image_url="/images/chicken_salad.jpg",
            ingredients="chicken,lettuce,tomato,cucumber,olive oil,lemon,salt,pepper",
            categories=cats("lunch"),
        )
        r3 = Recipe(
            title="Chocolate Brownies",
            description="Rich and fudgy brownies.",
            instructions="Mix ingredients, bake at 350°F for 25-30 minutes.",
            image_url="/images/brownies.jpg",
            ingredients="chocolate,flour,sugar,eggs,butter,cocoa powder,salt",
            categories=cats("dessert"),
        )
        db.add_all([r1, r2, r3])
        db.commit()

@app.on_event("startup")
def on_startup():
    # Create tables
    Base.metadata.create_all(bind=engine)
    # Seed data
    with next(get_db()) as db:
        seed_data(db)
