from fastapi import FastAPI ,APIRouter,Depends,UploadFile,status,Request
from fastapi.responses import JSONResponse
from helpers.config import get_setting,settings
from controllers import DataController,ProjectController,ProcessController
from models import ResponseSignal
import aiofiles
import os
from .schemes.data import prepocessRequest
import logging
from models.Project_model import ProjectModel
from models.chunk_model import ChunkModel
from models.db_schemes import ChunkData

logger=logging.getLogger('uvicorn.error')

data_router=APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1","data"]
)

@data_router.post("/upload/{project_id}")
# request will get all information about the request included db_client
async def upload_data(request:Request,project_id:str,file:UploadFile,
                      app_setting:settings=Depends(get_setting)):


    project_model=ProjectModel(
        db_client= request.app.db_client
    )

    project=await project_model.get_project_or_create_one(
        project_id=project_id
    )

    data_obj=DataController()
    is_valied,result_signal=data_obj.validate_uploaded_file(file=file)


    if not is_valied:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal":result_signal
            }
        )
    
    project_dir_path=ProjectController().Get_project_path(project_id=project_id)

    file_path,file_id=data_obj.generate_unique_filepath(
        orig_file_name=file.filename,
        project_id=project_id
    )
    
    # file_path=os.path.join(
    #     project_dir_path,
    #     file.filename
    # )


    try:
        async with aiofiles.open(file_path,'wb') as f:
            while chunk := await file.read(app_setting.FILE_DEFAULT_CHUNK_SIZE):
                await f.write (chunk)

    except Exception as e:
         logger.error(f"Error while uploading file :{e}")
         return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal":ResponseSignal.FILE_UPLOAD_FAILED.value
            }
        )

    return JSONResponse(
       
        content={
            "signal":ResponseSignal.FILE_UPLOADED_SUCCESS.value,
            "file_id":file_id
    
        }
    )




@data_router.post("/process/{project_id}")
async def process_endpoint(request:Request,project_id:str,process_req:prepocessRequest):
    file_id=process_req.file_id
    chunk_size=process_req.chunk_size
    overlap_size=process_req.overlap_size
    do_reset=process_req.do_reset

    project_model=ProjectModel(
        db_client= request.app.db_client
    )

  
    project=await project_model.get_project_or_create_one(
        project_id=project_id
    )

    

    process_controller=ProcessController(project_id)

    file_content=process_controller.get_file_content(file_id=file_id)

    file_chunks=process_controller.process_file_content(file_content=file_content,
                                                   file_id=file_id,chunk_size=chunk_size,
                                                   overlap_size=overlap_size)
    

    if file_chunks is None or len(file_chunks)==0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal":ResponseSignal.PROCESSING_FAILED.value
            }
        )
    

    file_chunks_records=[
        ChunkData(
            chunk_text=chunk.page_content,
            chunk_order=i+1,
            chunk_metadata=chunk.metadata,
            chunk_project_id=project.id
        )
        for i,chunk in enumerate(file_chunks)
    ]
    
    chunk_model=ChunkModel(
        db_client= request.app.db_client
    )

    if do_reset==1:
        _=await chunk_model.delete_chunks_by_project_id(
        project_id=project.id

        )


    no_records=await chunk_model.insert_many_chunks(chunks=file_chunks_records)

    return JSONResponse(
        content={
                "signal":ResponseSignal.PROCESSING_SUCCESS.value,
                "inserted_chunks":no_records
        }
    )

