from fastapi import APIRouter,UploadFile,File,Form
from typing import List
from .. import schemas
from .. import model

router = APIRouter(prefix="/level1/training",tags=["Level 1 training"])

@router.get("/{user_id}",response_model= List[schemas.numbered_training_data],tags=["Level 1 training"])
def get_level_1_data(user_id:str):
    return model.get_training_data(user_id=user_id,level_num=1)


