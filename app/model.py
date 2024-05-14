from pathlib import Path
import speech_recognition as sr
from . import schemas
import json
from sentence_transformers import util
from fastapi.responses import JSONResponse
from fastapi import UploadFile
from sentence_transformers import SentenceTransformer
from . import database


model_name = "paraphrase-multilingual-MiniLM-L12-v2"
model = SentenceTransformer(model_name)

# Load the trained model
BASE_DIR = Path(__file__).resolve(strict=True).parent

# Open the JSON file
with open(f"{BASE_DIR}/data/sentences.json","r") as file:
    # Load the JSON data into a Python dictionary
    sentences = json.load(file)
# Open the JSON file
with open(f"{BASE_DIR}/data/images.json","r") as file:
    # Load the JSON data into a Python dictionary
    images = json.load(file)

# Open the JSON file
with open(f"{BASE_DIR}/data/audios.json","r") as file:
    # Load the JSON data into a Python dictionary
    audios = json.load(file)



###################
#other functions
###################

def get_audio(level_num : str,audio_name:str) ->str:
    audio = audios[f"level_{level_num}"][audio_name]

    if audio!= None:
        return audio
    else:
        raise NameError(f"audio '{audio_name}' for level {level_num} not found.")


def get_advanced_audio(audio_class:str,audio_name:str) ->str:
    audio = audios["advanced"][audio_class][audio_name]

    if audio!= None:
        return audio
    else:
        raise NameError(f"audio '{audio_name}' for {audio_class} class in advanced level not found.")


def get_image(level_num : str,image_name:str) ->str:
    image = images[f"level_{level_num}"][image_name]

    if image!= None:
        return image
    else:
        raise NameError(f"image '{image_name}' for level {level_num} not found.")

def get_name (level :int ,id:str):
    name = {
        "sub_level_name_ar": None,
        "sub_level_name_en": None
    }

    if level ==1 :
        name["sub_level_name_en"] = sentences["level_1"][id]
    elif level == 2 :
        name["sub_level_name_en"] = sentences["level_2"][id][0]
    else :
        name["sub_level_name_ar"] = sentences["advanced"][id]["name_ar"]
        name["sub_level_name_en"] = sentences["advanced"][id]["name_en"]
    return name


def get_sub_level1_data (user_id:str,id:int) -> schemas.level1_training_data:
    object_name = sentences["level_1"][f"{id}"]
    image = get_image(1,object_name)
    audio = get_audio(1,object_name)
    available = is_available(user_id,1,id)
    level_1_data = schemas.level1_training_data(available=available
                                                ,animal_name=object_name
                                                ,image_url=image
                                                ,audio_url=audio)
    return level_1_data

def get_training_data(user_id : str,level_num:int) -> list[schemas.numbered_training_data]:
    number_of_sentences = len(sentences[f"level_{level_num}"])
    training_data = []
    for i in range(1,number_of_sentences+1):
        details = get_sub_level1_data(user_id=user_id,id = i)
        value = schemas.numbered_training_data(id = i,details=details)
        training_data.append(value)
    return training_data


def get_sub_level2_data (user_id:str,id:int) -> schemas.level2_training_data:
    object_name = sentences[f"level_{2}"][f"{id}"][0]
    sentence = sentences[f"level_{2}"][f"{id}"][1]
    image = get_image(2,object_name)
    audio = get_audio(2,object_name)
    available = is_available(user_id,2,id)
    level_2_data = schemas.level2_training_data(available=available,
                                                shape_name=object_name,
                                                sentence=sentence,
                                                image_url=image,
                                                audio_url=audio)
    return level_2_data


def get_level2_training_data (user_id : str,level_num:int) ->list[schemas.numbered_level2_training]:
    number_of_sentences = len(sentences[f"level_{level_num}"])
    training_data = []
    for i in range(1,number_of_sentences+1):
        details = get_sub_level2_data(user_id=user_id,id=i)
        value = schemas.numbered_level2_training(id = i,details=details)
        training_data.append(value)
    return training_data

def get_sub_advanced_level_data (id:int) -> schemas.numbered_advanced_level:
    bismillah_ar = sentences["advanced"]["0"]["ar"]
    bismillah_en = sentences["advanced"]["0"]["en"]
    bismillah_audio_url = get_advanced_audio("0","1")
    surah = sentences["advanced"][f"{id}"]
    surah_name_ar = surah["name_ar"]
    surah_name_en = surah["name_en"]
    type_ar = surah["type"]
    type_en = surah["type_en"]
    ayahs_num = surah["Ayahs"]
    surah_content_arabic = surah["ar"]
    surah_content_english = surah["en"]
    full_surah = []
    complete_ayah_info = schemas.surah_content(ayah_num=0,ayah_ar=bismillah_ar
                                                ,ayah_en=bismillah_en
                                                ,ayah_audio_url=bismillah_audio_url)
    full_surah.append(complete_ayah_info)
    for j in range(0,len(surah_content_arabic)):
        ayah_num = j+1
        ayah_ar = surah_content_arabic[j]
        ayah_en = surah_content_english[j]
        ayah_audio_url = get_advanced_audio(f"{id}",f"{ayah_num}")
        complete_ayah_info = schemas.surah_content(ayah_num=ayah_num,ayah_ar=ayah_ar,ayah_en=ayah_en,ayah_audio_url=ayah_audio_url)
        full_surah.append(complete_ayah_info)
    all_data = schemas.advanced_level(surah_name_ar=surah_name_ar,surah_name_en=surah_name_en,
                                        type_ar=type_ar,type_en=type_en,ayahs_num=ayahs_num,
                                        full_surah=full_surah)
    numberd_data = schemas.numbered_advanced_level(id=id,details=all_data)
    return numberd_data

def get_advanced_level_data()->list[schemas.numbered_advanced_level]:
    number_of_surahs = len(sentences["advanced"])
    data = []
    for i in range(1,number_of_surahs):
        numberd_data = get_sub_advanced_level_data(id=i)
        data.append(numberd_data)
    return data

def STL(audio_file:UploadFile,level:int = 1):
    r = sr.Recognizer()
    transcriptions = []
    if level == 3 :
        language = 'ar-AR'
    else:
        language = 'en-US'

    with sr.AudioFile(audio_file) as source:
        audio = r.record(source)
    t = r.recognize_google(audio, language= language)  # Recognize English speech
    transcriptions.append(t)

    return transcriptions

def calculate_average_similarity(sentences: list, transcriptions: list):
    sentence_embeddings1 = model.encode(sentences, convert_to_tensor=True)
    transcriptions_embeddings = model.encode(transcriptions, convert_to_tensor=True)

    # Move tensors to CPU before converting to NumPy arrays
    sentence_embeddings1 = sentence_embeddings1.cpu()
    transcriptions_embeddings = transcriptions_embeddings.cpu()

    similarities = util.pytorch_cos_sim(sentence_embeddings1, transcriptions_embeddings).numpy().diagonal()
    average_similarity = sum(similarities) / len(similarities)

    return average_similarity


########################
#database part
########################
db = database.db
user_authorization = db["User Authorization"]
def is_available (id :str,level_num:int,suplevel:int,update:bool=False):
    # Check if the document with the provided ID exists in the collection
    document = user_authorization.find_one({"_id": id})
    if document:
        if update:
            # Check if the previous suplevels are set to 1
            for i in range(1, suplevel):
                if document.get(f"level{level_num}", {}).get(str(i), 0) != 1:
                    # If any previous suplevel is not set to 1, return error response
                    # return False
                    return JSONResponse(status_code=400, content={"Error": "You need to succeed in the previous suplevels to open the next."})

            # Update specific level and sublevel
            update_field = f"level{level_num}"
            update_query = {"_id": id}
            set_query = {f"{update_field}.{suplevel}": 1}
            
            user_authorization.update_one(update_query, {"$set": set_query})
            # return True
            return JSONResponse(status_code=200, content={"message": f"Congratulations! You have successfully completed stage {suplevel} and are now eligible to proceed to the next stage."})
        
        else:
            return document.get(f"level{level_num}",{}).get(str(suplevel),0)
    else:
        # If document doesn't exist, create a new document
        # Calculate the number of sentences
        number_of_sentences_level1 = len(sentences["level_1"])
        number_of_sentences_level2 = len(sentences["level_2"])
        # Initialize fields for level1 and level2
        level1 = {str(i + 1): 1 if i == 0 else 0 for i in range(number_of_sentences_level1)}
        level2 = {str(i + 1): 1 if i == 0 else 0 for i in range(number_of_sentences_level2)}

        # Create a new document with the provided ID and initialized fields
        new_document = {"_id": id, "level1": level1, "level2": level2}
        user_authorization.insert_one(new_document)
        return True


history_collection = db["History"]

def update_user_history(user_id, level, sub_level=1,ayah_num = 0, accuracy=0):
    # Check if the document with the provided ID exists in the collection
    document = history_collection.find_one({"_id": user_id})
    if document:
        # Get the current highest accuracy for the sub-level
        # Get the sub-level data for the specified level
        sub_level_data = document.get(f'level{level}', {}).get(str(sub_level), {})

        # Get the highest accuracy for the specified sub-level
        current_highest_accuracy = sub_level_data.get('highest_accuracy')
        if(level == 3):
            current_highest_accuracy = sub_level_data.get(f'{ayah_num}',{}).get('highest_accuracy')
        # Initialize to 0 if highest accuracy is None
        if current_highest_accuracy is None:
            current_highest_accuracy = 0
        # Update the document only if the new accuracy is higher
        if accuracy > current_highest_accuracy:
            if level == 3 :
                result = history_collection.update_one(
                {'_id': user_id},
                {'$set': {
                    f'level{level}.{sub_level}.{ayah_num}.highest_accuracy': accuracy
                }},
                upsert=True
            )
            else:
                result = history_collection.update_one(
                    {'_id': user_id},
                    {'$set': {
                        f'level{level}.{sub_level}.highest_accuracy': accuracy
                    }},
                    upsert=True
                )

        
    else:
        # If document doesn't exist, create a new document
        # Calculate the number of sentences

        number_of_sentences_level1 = len(sentences["level_1"])
        number_of_sentences_level2 = len(sentences["level_2"])
        number_of_sentences_level3 = len(sentences["advanced"])
        # Initialize fields for level1 and level2
        level1 = {str(i + 1): {'highest_accuracy': 0} for i in range(number_of_sentences_level1)}
        level2 = {str(i + 1): {'highest_accuracy': 0} for i in range(number_of_sentences_level2)}
        level3 ={}
        for i in range(1,number_of_sentences_level3):
            surah = sentences["advanced"][f"{i}"]
            ayahs_num = surah["Ayahs"]
            surah_details = {}
            for j in range(ayahs_num+1):
                surah_details[str(j)]={'highest_accuracy': 0}
            level3[str(i)]=surah_details
        # Create a new document with the provided ID and initialized fields
        new_document = {"_id": user_id, "level1": level1, "level2": level2,"level3":level3}
        history_collection.insert_one(new_document)
        update_user_history(user_id=user_id,level=level,sub_level=sub_level,ayah_num=ayah_num,accuracy=accuracy)    



def get_accuracy_details(document,user_id: str, level: int) -> schemas.accuricy_analysis:
    
    # Extract accuracy details for the specified level
    level_data = document.get(f'level{level}')
    if level_data:
        sub_levels_keys = list(level_data.keys())  # Get list of sub-level keys
        level_total_score = 0.0
        sub_levels = []
        for key in sub_levels_keys:
            sub_level_name = get_name(level=level, id=key)
            sub_level_percent = 0.0
            if level == 1 or level == 2:
                sub_level_image_url = get_image(str(level), sub_level_name["sub_level_name_en"])
                sub_level_percent = level_data[key].get('highest_accuracy', 0)
            else:
                sub_level_image_url = None
                for ayah_num in range (len(level_data[key])+1):
                    sub_level_percent += level_data[key].get(f'{ayah_num}',{}).get('highest_accuracy', 0)
                sub_level_percent = round(sub_level_percent/len(level_data[key]),2)
            level_total_score += sub_level_percent
            
            sub_level_details = {
                "sub_level_name_ar": sub_level_name["sub_level_name_ar"],
                "sub_level_name_en" : sub_level_name["sub_level_name_en"],
                "sub_level_image_url": sub_level_image_url,
                "sub_level_percent": sub_level_percent
            }
            sub_levels.append(sub_level_details)

        # Create an accuracy_analysis object for the current level
        accuracy_details = schemas.accuricy_analysis(
            level=level,
            sub_levels=sub_levels,
            level_total_score=round(level_total_score/len(sub_levels_keys),2)
        )
        return accuracy_details
