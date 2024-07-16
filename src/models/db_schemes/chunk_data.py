from pydantic import BaseModel,Field,validator
from typing import Optional
from bson.objectid import ObjectId


class ChunkData(BaseModel):
    id:Optional[ObjectId]=Field(None,alias="_id")  #this _id it understand that thid attrubite is private so we will use allis
    # use here None not ... becuse this not require Field

    chunk_text:str =Field(...,min_length=1)
    chunk_order:int=Field(...,gt=0)
    chunk_metadata:dict
    chunk_project_id: ObjectId


    class Config: # to ignore any un know data type like 'ObjectId'
        arbitrary_types_allowed = True
        