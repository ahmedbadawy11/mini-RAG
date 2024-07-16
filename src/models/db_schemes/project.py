from pydantic import BaseModel,Field,validator
from typing import Optional
from bson.objectid import ObjectId

class project(BaseModel):
    id:Optional[ObjectId]=Field(None,alias="_id") 
    project_id: str=Field(...,min_length=1)


    @validator('project_id')
    def validate_project_id(cls,value):
        if not value.isalnum():
            raise ValueError ('Project_id Must be alphanumeric')
        
        return value
    

    class Config: # to ignore any un know data type like 'ObjectId'
        arbitrary_types_allowed = True
        



