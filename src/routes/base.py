from fastapi import FastAPI ,APIRouter,Depends
from helpers.config import get_setting,settings
import os

base_router=APIRouter(
    prefix="/api/v1",
    tags=["api_v1"]
)

@base_router.get('/')
async def welcome(app_setting:settings=Depends(get_setting)):
    
    app_name=app_setting.APP_NAME
    app_version=app_setting.APP_VERSION
    # app_allow=app_setting.FILE_ALLOWED_TYPES
    return{
        'app_name':app_name,
        'app_version':app_version,
        # 'app_allow':app_allow
    }

