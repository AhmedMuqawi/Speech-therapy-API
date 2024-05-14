from fastapi import APIRouter
from typing import List
from .. import schemas

router = APIRouter(prefix="/levels",tags=["Levels"])

levels = [
    {
        "level": "Level One",
        "description" : "learn the name and the shape of animal",
        "image_url": "https://res.cloudinary.com/dkeeazjre/image/upload/v1714133678/Photos/dkmeuvmecscouk6gemwd.jpg"
    },
    {
        "level": "Level Two",
        "description" : "learn the aboutGeometric forms",
        "image_url": "https://res.cloudinary.com/dkeeazjre/image/upload/v1714133680/Photos/kpxrnbq8ibbdluebfqlx.jpg"
    },
    {
        "level": "Advanced Level",
        "description" : "learn the holy quran",
        "image_url": "https://res.cloudinary.com/dkeeazjre/image/upload/v1714133702/Photos/mct9klf4bntjp6kxflaz.jpg"
    }
]


@router.get("/",response_model= List[schemas.levels])
def get_levels():
    data = []
    for level in levels:
        data.append(schemas.levels(**level))
    return data

    

