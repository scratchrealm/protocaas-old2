from pydantic import BaseSettings
import os


class Settings(BaseSettings):
    # General app config
    MONGO_URI = os.environ.get("MONGO_URI")
    
    PUBNUB_SUBSCRIBE_KEY = os.environ.get("VITE_PUBNUB_SUBSCRIBE_KEY")
    PUBNUB_PUBLISH_KEY = os.environ.get("PUBNUB_PUBLISH_KEY")
    
    GITHUB_CLIENT_ID = os.environ.get("VITE_GITHUB_CLIENT_ID")
    GITHUB_CLIENT_SECRET = os.environ.get("GITHUB_CLIENT_SECRET")
    
    DEFAULT_COUPUTE_RESOURCE_ID = os.environ.get("VITE_DEFAULT_COUPUTE_RESOURCE_ID")

    OUTPUT_BUCKET_URI = os.environ.get("OUTPUT_BUCKET_URI")
    OUTPUT_BUCKET_CREDENTIALS = os.environ.get("OUTPUT_BUCKET_CREDENTIALS")
    OUTPUT_BUCKET_BASE_URL = os.environ.get("OUTPUT_BUCKET_BASE_URL")

def get_settings():
    return Settings()