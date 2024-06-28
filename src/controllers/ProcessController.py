from .BaseController import BaseController
from .ProjectController import ProjectController
import os
from models import ProcessEnum

from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

class ProcessController(BaseController):

    def __init__(self,project_id):
        super().__init__()
        self.project_id=project_id
        self.project_path=ProjectController().Get_project_path(project_id)

    def get_file_extension (self,file_id:str):
        return os.path.splitext(file_id)[-1]


    def get_fileloader(self,file_id:str):
        
        file_ext=self.get_file_extension(file_id=file_id)

        file_path=os.path.join(
            self.project_path,
            file_id
        )
        if file_ext==ProcessEnum.TXT.value:

            return TextLoader(file_path,encoding="utf-8")
        
        if file_ext==ProcessEnum.PDF.value:

            return PyMuPDFLoader(file_path)
        
        return None
    

    def get_file_content(self,file_id:str):
        loader=self.get_fileloader(file_id=file_id)

        return loader.load()
    
    def process_file_content(self,file_content: list,file_id:str,
                             chunk_size:int=100,overlap_size:int=20):
        
        text_splitters=RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap_size,
            length_function=len

        )

        file_content_text=[doc.page_content  for doc in file_content]
        file_content_meta_data=[doc.metadata  for doc in file_content]

        chunks=text_splitters.create_documents(
            file_content_text,
            metadatas=file_content_meta_data
        )

        return chunks