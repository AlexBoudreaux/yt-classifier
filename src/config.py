import os
from dotenv import load_dotenv

try:
    load_dotenv()
except Exception as e:
    logging.error(f"Error loading .env file: {str(e)}", exc_info=True)
    raise

# YouTube API
DEVELOPER_KEY = os.getenv("YOUTUBE_API_KEY")
if not DEVELOPER_KEY:
    logging.error("YOUTUBE_API_KEY is not set in the environment variables.")
    raise EnvironmentError("YOUTUBE_API_KEY is not set in the environment variables.")
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# Chrome Profile Path
PROFILE_PATH = os.getenv("CHROME_PROFILE_PATH")
if not PROFILE_PATH:
    logging.error("CHROME_PROFILE_PATH is not set in the environment variables.")
    raise EnvironmentError("CHROME_PROFILE_PATH is not set in the environment variables.")

# OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logging.error("OPENAI_API_KEY is not set in the environment variables.")
    raise EnvironmentError("OPENAI_API_KEY is not set in the environment variables.")

# Pinecone API Key
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
if not PINECONE_API_KEY:
    logging.error("PINECONE_API_KEY is not set in the environment variables.")
    raise EnvironmentError("PINECONE_API_KEY is not set in the environment variables.")

# Firebase Admin SDK file path
FIREBASE_ADMIN_SDK_PATH = os.getenv("FIREBASE_ADMIN_SDK_PATH")
if not FIREBASE_ADMIN_SDK_PATH:
    logging.error("FIREBASE_ADMIN_SDK_PATH is not set in the environment variables.")
    raise EnvironmentError("FIREBASE_ADMIN_SDK_PATH is not set in the environment variables.")
