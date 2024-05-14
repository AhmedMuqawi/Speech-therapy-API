import os
from pymongo import MongoClient

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the MongoDB connection URI from environment variables
MONGODB_URI = os.getenv("MONGODB_URI")

if MONGODB_URI is None:
    raise ValueError("MongoDB connection URI is not set in environment variables.")

# Connect to the MongoDB database  for medical data
client = MongoClient(MONGODB_URI)

# Access the database for medical data
db = client["Speech_Therapy"]
