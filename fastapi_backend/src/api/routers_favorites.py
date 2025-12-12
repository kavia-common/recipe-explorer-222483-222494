from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .db import get_db
from .models import Favorite, Recipe, User
from .schemas import Favorite as FavoriteSchema, FavoriteCreate
from .auth import get_current_user

router = APIRouter(prefix="/users", tags=["favorites"])

@router.get("/{user_id}/favorites", response_model=list[FavoriteSchema], summary="List favorites", description="List a user's favorite recipes")
def list_favorites(user_id: int, db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    if current.id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    favs = db.query(Favorite).filter(Favorite.user_id == user_id).all()
    return favs

@router.post("/{user_id}/favorites", response_model=FavoriteSchema, summary="Add favorite", description="Favorite a recipe")
def add_favorite(user_id: int, payload: FavoriteCreate, db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    if current.id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    recipe = db.query(Recipe).filter(Recipe.id == payload.recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    existing = db.query(Favorite).filter(Favorite.user_id == user_id, Favorite.recipe_id == payload.recipe_id).first()
    if existing:
        return existing
    fav = Favorite(user_id=user_id, recipe_id=payload.recipe_id)
    db.add(fav)
    db.commit()
    db.refresh(fav)
    return fav

@router.delete("/{user_id}/favorites/{recipe_id}", summary="Remove favorite", description="Remove a recipe from favorites")
def remove_favorite(user_id: int, recipe_id: int, db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    if current.id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    fav = db.query(Favorite).filter(Favorite.user_id == user_id, Favorite.recipe_id == recipe_id).first()
    if not fav:
        raise HTTPException(status_code=404, detail="Favorite not found")
    db.delete(fav)
    db.commit()
    return {"status": "ok"}
