from fastapi import APIRouter
from typing import List
from .. import schemas
from .. import model

router = APIRouter(prefix="/level2/training",tags=["Level 2 training"])

@router.get("/{user_id}",response_model= List[schemas.numbered_level2_training],tags=["Level 2 training"])
def get_level_2_data(user_id:str):
    return model.get_level2_training_data(user_id=user_id,level_num=2)


