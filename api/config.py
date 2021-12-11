from pydantic import BaseSettings,Field
from functools import lru_cache

class Settings(BaseSettings):
    twilio_account_sid : str = Field(...,env='TWILIO_ACCOUNT_SID')
    twilio_auth_token : str = Field(...,env='TWILIO_AUTH_TOKEN')
    twilio_service_id : str = Field(...,env='TWILIO_SERVICE_ID')
    app_secret : str = Field(...,env='APP_SECRET')
    symbl_app_id : str = Field(...,env='SYMBL_APP_ID')
    symbl_app_secret : str = Field(...,env='SYMBL_APP_SECRET')

    #redis_url : str = Field(...,env='REDIS_URL')

    class Config:
        env_file = '.env'

@lru_cache
def get_settings():
    return Settings()