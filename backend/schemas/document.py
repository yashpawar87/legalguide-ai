from pydantic import BaseModel


class DocumentCreate(BaseModel):
    title: str
    content: str
    user_id: str

    
