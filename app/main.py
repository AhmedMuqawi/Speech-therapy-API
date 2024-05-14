from fastapi import FastAPI, UploadFile
from fastapi.responses import JSONResponse
from . import model
from .router import levels , level_1_training , level_2_training , advanced_level
from . import schemas

app = FastAPI()

############################
# levels
############################
app.include_router(levels.router)
############################
# level one training
############################
app.include_router(level_1_training.router)
############################
# level two training
############################
app.include_router(level_2_training.router)
############################
# advanced level training
############################
app.include_router(advanced_level.router)

incorrect = "https://res.cloudinary.com/dkeeazjre/image/upload/v1713357298/Photos/r4bpw1ynrpkrour8zxm0.jpg"
correct = "https://res.cloudinary.com/dkeeazjre/image/upload/v1713357312/Photos/uavtmpzhtn5xr3n1omzj.jpg"

@app.post("/marking/",response_model=schemas.marking_level1_and_2,tags=["Level 1&2 Marking"])
def marking (user_id:str,level:int,id: int ,audio_file:UploadFile):
    image_name = []
    if level ==1 :
        temp = model.sentences["level_1"][f"{id}"].lower()
    elif level ==2:
        temp = model.sentences["level_2"][f"{id}"][1]

    else:
        return JSONResponse(content={"Error": "Please enter the right level number."}, status_code=400)
    available = model.is_available(user_id,level,id)
    if(available==0):
        return JSONResponse(content={"Error": "You need to succeed in the previous suplevels to open this one."}, status_code=400)
    image_name.append(temp)
    try: 
        transcription = model.STL(audio_file.file)
    except Exception as e:
        if (str(e)==""):
            return JSONResponse(content={"Error": "Please try again in a quiet environment and speak a bit louder."}, status_code=400)
        return JSONResponse(content={"Error": str(e)}, status_code=400)
   
    similarity = model.calculate_average_similarity(image_name,transcription)
    similarity_percent = round(similarity,2) * 100  
    model.update_user_history(user_id=user_id,level=level,sub_level=id,accuracy=similarity_percent)
    if similarity_percent>=60 :
        status = "Great job! You've made significant progress. Keep up the positive momentum and let's tackle the next challenge together!"
        length = len(model.sentences[f"level_{level}"])
        if(id < length):
            available = model.is_available(user_id,level,id+1)
            if available==0:
                model.is_available(user_id,level,id+1,update=True)
            next_sub_level = None
            if level==1:
                _id = id+1 
                level_1_data = model.get_sub_level1_data(user_id=user_id,id=_id)
                numbered_training_data = schemas.numbered_training_data(id=_id,details=level_1_data)
                next_sub_level = schemas.next_sub_level(levelOneDetails=numbered_training_data) 
            else :
                _id = id+1 
                level_2_data = model.get_sub_level2_data(user_id=user_id,id=_id) 
                numbered_level2_training = schemas.numbered_level2_training(id=_id,details=level_2_data)              
                next_sub_level = schemas.next_sub_level(levelTwoDetails=numbered_level2_training) 
            result = schemas.marking_level1_and_2(next=next_sub_level,status=status,percent=similarity_percent,image_url=correct)
        else:
            result = schemas.marking_level1_and_2(next=None,status=status,percent=similarity_percent,image_url=correct)
        return result
    else:
        status = "Don't worry, you're making progress! While this attempt didn't meet the goal, remember that every step forward is a step closer to success. Keep going!"
        length = len(model.sentences[f"level_{level}"])
        result = schemas.marking_level1_and_2(status=status,percent=similarity_percent,image_url=incorrect)
        if(id < length):
            available = model.is_available(user_id,level,id+1)
            if available==1:
                _id = id+1
                if level==1:
                    level_1_data = model.get_sub_level1_data(user_id=user_id,id=_id)
                    numbered_training_data = schemas.numbered_training_data(id=_id,details=level_1_data)
                    next_sub_level = schemas.next_sub_level(id=_id,details=level_1_data) 
                    result.next = next_sub_level
                else:
                    level_2_data = model.get_sub_level1_data(user_id=user_id,id=_id) 
                    numbered_level2_training = schemas.numbered_level2_training(id=_id,details=level_2_data)              
                    next_sub_level = schemas.next_sub_level(id=_id,details=level_2_data) 
                    result.next = next_sub_level
        else:
            result.next= None
        return result

@app.post("/advanced/marking/",response_model=schemas.marking,tags=["Advanced Level Marking"])
def marking (user_id:str,id: int,ayah_num:int ,audio_file:UploadFile):
    image_name = []
    temp = model.sentences["advanced_validation"][f"{id}"][f"{ayah_num}"]
    image_name.append(temp)
    try: 
        transcription = model.STL(audio_file.file,3)
    except Exception as e:
        if (str(e)==""):
            return JSONResponse(content={"Error": "Please try again in a quiet environment and speak a bit louder."}, status_code=400)
        return JSONResponse(content={"Error": str(e)}, status_code=400)
    print(image_name)
    print(transcription)
    similarity = model.calculate_average_similarity(image_name,transcription)
    similarity_percent = round(similarity,2) * 100   
    model.update_user_history(user_id=user_id,level=3,sub_level=id,ayah_num=ayah_num,accuracy=similarity_percent) 
    status = "Great job! You've made significant progress. Keep up the positive momentum and let's tackle the next challenge together!" if similarity_percent >= 70 else "Don't worry, you're making progress! While this attempt didn't meet the goal, remember that every step forward is a step closer to success. Keep going!"
    image_url = correct if similarity_percent >= 70 else incorrect
    result = schemas.marking(status=status,percent=similarity_percent,image_url=image_url)
    return result



@app.get("/score/",response_model=schemas.accuricy_analysis,tags=["Total Score"])
def score (user_id:str,level: int ):
    # Query the database to get accuracy details
    document = model.history_collection.find_one({"_id": user_id})
    if document:
        return model.get_accuracy_details(document=document,user_id=user_id,level=level)
    else:
        model.update_user_history(user_id=user_id,level=level)
        document = model.history_collection.find_one({"_id": user_id})
        return model.get_accuracy_details(document=document,user_id=user_id,level=level)