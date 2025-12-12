from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .db import get_db
from .models import Recipe, Category
from .schemas import Recipe as RecipeSchema

router = APIRouter(prefix="/recipes", tags=["recipes"])

@router.get("/", response_model=List[RecipeSchema], summary="List recipes", description="List recipes with optional filtering by category")
def list_recipes(category_id: Optional[int] = None, db: Session = Depends(get_db)):
    q = db.query(Recipe)
    if category_id:
        q = q.join(Recipe.categories).filter(Category.id == category_id)
    return q.order_by(Recipe.created_at.desc()).all()

@router.get("/{recipe_id}", response_model=RecipeSchema, summary="Recipe details", description="Get a single recipe by ID")
def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    r = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return r

@router.get("/search/by", response_model=List[RecipeSchema], summary="Search recipes", description="Search by name or ingredients (comma-separated)")
def search_recipes(q: Optional[str] = Query(None, description="Search query"),
                   ingredients: Optional[str] = Query(None, description="Comma separated ingredients"),
                   db: Session = Depends(get_db)):
    query = db.query(Recipe)
    if q:
        like = f"%{q.lower()}%"
        query = query.filter(Recipe.title.ilike(like) | Recipe.description.ilike(like))
    if ingredients:
        parts = [p.strip().lower() for p in ingredients.split(",") if p.strip()]
        for p in parts:
            like = f"%{p}%"
            query = query.filter(Recipe.ingredients.ilike(like))
    return query.order_by(Recipe.created_at.desc()).all()
