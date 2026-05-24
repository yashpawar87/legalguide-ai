import os
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File
)
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
from langchain.text_splitter import RecursiveCharacterTextSplitter
from ai.rag.retriever import get_qdrant_client
import uuid

from backend.db.deps import get_db
from backend.model.document import Document
from backend.schemas.document import DocumentCreate
from backend.api.v1.auth import verify_token

router = APIRouter()

@router.post("/")
async def create_document(
    payload: DocumentCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(verify_token)
):
    document = Document(
        title=payload.title,
        content=payload.content,
        user_id=user["uid"]
    )

    db.add(document)

    db.commit()

    db.refresh(document)

    return {
        "id": document.id,
        "title": document.title,
        "content": document.content,
        "user_id": document.user_id
    }


@router.get("/")
async def get_documents(
    db: Session = Depends(get_db),
    user: dict = Depends(verify_token)
):
    documents = db.query(Document).filter(Document.user_id == user["uid"]).all()

    return [
        {
            "id": doc.id,
            "title": doc.title,
            "content": doc.content,
            "user_id": doc.user_id
        }
        for doc in documents
    ]


@router.get("/{document_id}")
async def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(verify_token)
):
    document = (
        db.query(Document)
        .filter(Document.id == document_id, Document.user_id == user["uid"])
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    return {
        "id": document.id,
        "title": document.title,
        "content": document.content,
        "user_id": document.user_id
    }


@router.put("/{document_id}")
async def update_document(
    document_id: int,
    payload: DocumentCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(verify_token)
):
    document = (
        db.query(Document)
        .filter(Document.id == document_id, Document.user_id == user["uid"])
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    document.title = payload.title
    document.content = payload.content

    db.commit()

    db.refresh(document)

    return {
        "id": document.id,
        "title": document.title,
        "content": document.content,
        "user_id": document.user_id
    }


@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(verify_token)
):
    document = (
        db.query(Document)
        .filter(Document.id == document_id, Document.user_id == user["uid"])
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    db.delete(document)

    db.commit()

    return {
        "message": "Document deleted"
    }


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: dict = Depends(verify_token)
):
    upload_dir = "data/uploads"

    os.makedirs(upload_dir, exist_ok=True)

    file_path = f"{upload_dir}/{file.filename}"

    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    document = Document(
        title=file.filename,
        filename=file.filename,
        file_path=file_path,
        user_id=user["uid"]
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    # --- TEXT EXTRACTION (OCR) ---
    extracted_text = ""
    try:
        if file.filename.lower().endswith(".pdf"):
            pdf_doc = fitz.open(file_path)
            for page in pdf_doc:
                extracted_text += page.get_text()
            pdf_doc.close()
        elif file.filename.lower().endswith((".png", ".jpg", ".jpeg")):
            img = Image.open(file_path)
            extracted_text = pytesseract.image_to_string(img)
    except Exception as e:
        print(f"Error during extraction: {e}")
        # We continue even if OCR fails to not break the upload, 
        # but the vector store will just get empty text.
        
    if extracted_text.strip():
        # --- CHUNKING ---
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_text(extracted_text)
        # --- NATIVE QDRANT INGESTION ---
        client = get_qdrant_client()
        
        ids = [str(uuid.uuid4()) for _ in chunks]
        metadata = [{
            "document_id": document.id,
            "user_id": document.user_id,
            "source": file.filename,
            "page_content": chunk # Fallback for old pipeline components
        } for chunk in chunks]
        
        try:
            # .add() automatically manages vector params, hashing, and parallel uploading
            client.add(
                collection_name="user_documents_collection",
                documents=chunks,
                metadata=metadata,
                ids=ids
            )
        except Exception as e:
            print(f"Failed to ingest to Qdrant: {e}")

    return {
        "id": document.id,
        "filename": document.filename,
        "file_path": document.file_path
    }