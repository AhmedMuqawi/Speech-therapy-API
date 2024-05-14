from fastapi import APIRouter
from typing import List
from .. import schemas
from .. import model

router = APIRouter(prefix="/advanced/training",tags=["advanced Level training"])

@router.get("/",response_model= List[schemas.numbered_advanced_level],tags=["advanced Level training"])
def get_advanced_level_data():
    return model.get_advanced_level_data()


