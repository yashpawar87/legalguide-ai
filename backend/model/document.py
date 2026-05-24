from sqlalchemy import Column, Integer, String

from backend.db.session import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)

    title = Column(String)

    content = Column(String)

    filename = Column(String)

    file_path = Column(String)

    user_id = Column(String)
    
    def __repr__(self):
        return f"<Document(id={self.id}, title='{self.title}')>"
    