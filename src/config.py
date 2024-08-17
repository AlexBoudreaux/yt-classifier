import os
from dotenv import load_dotenv

load_dotenv()

# YouTube API
DEVELOPER_KEY = os.getenv("YOUTUBE_API_KEY")
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# Chrome Profile Path
PROFILE_PATH = os.getenv("CHROME_PROFILE_PATH")

# OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Pinecone API Key
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

# Firebase Admin SDK file path
FIREBASE_ADMIN_SDK_PATH = os.getenv("FIREBASE_ADMIN_SDK_PATH")
