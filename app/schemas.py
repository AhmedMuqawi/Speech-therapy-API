from pydantic import BaseModel
from typing import List, Dict, Union


#create pydantic model for levels
class levels(BaseModel):
    level : str
    description : str
    image_url : str

# create a pydantic class for the taining data
class level1_training_data(BaseModel):
    available : bool
    animal_name : str
    image_url : str
    audio_url : str

class numbered_training_data(BaseModel):
    level:int=1
    id : int
    details : level1_training_data


# create a pydantic model for level2 training data
class level2_training_data(BaseModel):
    available : bool
    shape_name : str
    sentence: str
    image_url : str
    audio_url : str
 

class numbered_level2_training(BaseModel):
    level:int=2
    id : int 
    details : level2_training_data


#creating a pydantic model for advanced level data
class surah_content(BaseModel):
    ayah_num:int
    ayah_ar:str
    ayah_en:str
    ayah_audio_url:str


class advanced_level(BaseModel):
    surah_name_ar:str
    surah_name_en:str
    type_ar:str
    type_en:str
    ayahs_num:int
    full_surah:List[surah_content]

class numbered_advanced_level(BaseModel):
    level:int=3
    id:int
    details:advanced_level

#creating pydantic model for marking
class marking(BaseModel):
    status : str
    percent : float
    image_url : str


class next_sub_level(BaseModel):
    levelOneDetails: numbered_training_data|None = None
    levelTwoDetails: numbered_level2_training|None= None

class marking_level1_and_2(marking):
    next : next_sub_level | None = None


#create pydantic model for accuricy history
class level_details (BaseModel):
    sub_level_name_ar : str | None = None
    sub_level_name_en : str
    sub_level_image_url : str | None = None 
    sub_level_percent : float

class accuricy_analysis(BaseModel):
    level :int
    sub_levels : List[level_details]
    level_total_score : float
