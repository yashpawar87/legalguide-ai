import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from ai.embeddings.embedding_model import get_embedding_model
from langchain_qdrant import Qdrant
from qdrant_client import QdrantClient
from langchain.schema import Document

from ai.ocr.pdf_parser import extract_text_from_pdf
from ai.ner.legal_ner import extract_entities

def process_pdf(pdf_path: str, index_dir: str = "data/qdrant_index"):
    print(f"--- Processing {pdf_path} ---")
    
    # 1. Extract Text
    pages = extract_text_from_pdf(pdf_path)
    full_text = "\n".join([page['text'] for page in pages])
    
    # 2. Extract NER Entities for Metadata
    print("Extracting legal entities for metadata...")
    entities = extract_entities(full_text)
    
    base_metadata = {
        "source": os.path.basename(pdf_path),
        "court_name": entities.get("court_name") or "Unknown",
        "party_names": ", ".join(entities.get("party_names", [])),
    }
    
    # 3. Initialize Text Splitter and Chunk
    print("Chunking text...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    
    all_documents = []
    for page in pages:
        page_metadata = base_metadata.copy()
        page_metadata["page_num"] = page["page_num"]
        page_metadata["extraction_method"] = page.get("extraction_method", "unknown")
        
        chunks = text_splitter.split_text(page["text"])
        for chunk in chunks:
            all_documents.append(Document(page_content=chunk, metadata=page_metadata))
            
    print(f"Created {len(all_documents)} chunks.")

    # 4. Initialize Embeddings and Vector Store
    embeddings = get_embedding_model()
    
    os.makedirs(index_dir, exist_ok=True)
    
    print(f"Upserting {len(all_documents)} chunks into Qdrant collection 'legal_docs'...")
    
    Qdrant.from_documents(
        documents=all_documents,
        embedding=embeddings,
        collection_name="legal_docs",
        path=index_dir
    )
        
    print(f"Ingestion complete! Index saved to '{index_dir}'\n")

if __name__ == "__main__":
    # Test the ingestion pipeline directly
    process_pdf("data/uploads/sample.pdf")
