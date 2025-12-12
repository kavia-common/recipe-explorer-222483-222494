from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .db import get_db
from .models import Category
from .schemas import Category as CategorySchema

router = APIRouter(prefix="/categories", tags=["categories"])

@router.get("/", response_model=list[CategorySchema], summary="List categories", description="Retrieve all recipe categories")
def list_categories(db: Session = Depends(get_db)):
    return db.query(Category).order_by(Category.name.asc()).all()
