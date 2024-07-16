from .BaseDataModel import BaseDataModel
from .db_schemes import chunk_data 
from .enums.DataBaseEnum import DataBaseEnum
from bson.objectid import ObjectId
from pymongo import InsertOne # this is the type of the operation 

class ChunkModel(BaseDataModel):

    def __init__(self,db_client:object):
        super().__init__(db_client)
        self.collection=self.db_client[DataBaseEnum.COLLECTION_CHUNK_NAME.value]

    async def create_chunk(self,chunk:chunk_data):
        result=await self.collection.insert_one(chunk.dict(by_alias=True, exclude_unset=True)) # this is the action of the operation 
        chunk._id=result.inserted_id
        return 
    
    async def get_chunk(self,chunk_id:str):
        record=await self.collection.find_one({
            "_id":ObjectId(chunk_id)
        })

        if record is None:
            return None
        
        return chunk_data(**record)
    
    async def insert_many_chunks(self,chunks:list,batch_size:int=100):   
        # i  cann't inser one by one is aheadic opration instead i use bulk_write

        for i in range(0,len(chunks),batch_size):
            batch=chunks[i:i+batch_size]


            operaton=[
                InsertOne(chunk.dict(by_alias=True, exclude_unset=True))
                for chunk in batch
            ]

            await self.collection.bulk_write(operaton)

        return len(chunks)

    async def delete_chunks_by_project_id(self,project_id:str):
        result= await self.collection.delete_many({
            "chunk_project_id":project_id
        })

        return result.deleted_count
        