from fastapi import FastAPI
from helpers.config import get_setting
from motor.motor_asyncio import AsyncIOMotorClient
from routes import base
from routes import data


app=FastAPI()

@app.on_event("startup")
async def strartup_db_client():
    setting=get_setting()
    app.mongo_conn=AsyncIOMotorClient(setting.MONGODB_URL)
    app.db_client=app.mongo_conn[setting.MONGODB_DATABASE_NAME]


@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongo_conn.close()

app.include_router(base.base_router)
app.include_router(data.data_router)

