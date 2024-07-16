from .BaseDataModel import BaseDataModel
from .db_schemes import project 
from .enums.DataBaseEnum import DataBaseEnum


class ProjectModel(BaseDataModel):

    def __init__(self,db_client:object):
        super().__init__(db_client)
        self.collection=self.db_client[DataBaseEnum.COLLECTION_PROJECT_NAME.value]

    async def create_project(self,project:project):
        result=await self.collection.insert_one(project.dict(by_alias=True, exclude_unset=True))# to use the alias when pathing to mongo
        project._id=result.inserted_id

        return project
    
    async def get_project_or_create_one(self,project_id:str):
        
        record=await self.collection.find_one({
            "project_id":project_id
        })

        if record is None:
            # create New Project
            new_project=project(project_id=project_id)
            new_project=await self.create_project(project=new_project)

            return new_project
        
        return project(**record) # this take every value from record (dict) and create project class
    
    async def get_all_projects(self,page:int=1,page_size:int=10):
        #count total number of documents

        total_documents= await self.collection.count_documents({}) # empty filter to count any record

        # calculate total number of pages
        total_pages=total_documents//page_size

        if total_pages % page_size >0:
            total_pages +=1

        cursor=self.collection.find().skip((page-1)*page_size).limit(page_size)# this not return data but return cursor

        projects=[]

        async for document in cursor:
            projects.append(
                project(**document)
            )

        return projects,total_pages


