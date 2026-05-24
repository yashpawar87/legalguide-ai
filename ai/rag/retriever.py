import os
from qdrant_client import QdrantClient
from qdrant_client.http import models
from langchain_core.documents import Document as LcDoc
from langchain_community.document_compressors.flashrank_rerank import FlashrankRerank

_qdrant_client = None
_flashranker = None

def get_reranker():
    global _flashranker
    if _flashranker is None:
        _flashranker = FlashrankRerank()
    return _flashranker

def get_qdrant_client(index_dir: str = "data/qdrant_index"):
    global _qdrant_client
    if _qdrant_client is None:
        if os.path.exists(index_dir):
            _qdrant_client = QdrantClient(path=index_dir)
        else:
            # Create a new local DB if it doesn't exist
            _qdrant_client = QdrantClient(path=index_dir)
        try:
            # Configure FastEmbed models for Dense and Sparse embeddings
            _qdrant_client.set_model("BAAI/bge-large-en-v1.5")
            _qdrant_client.set_sparse_model("Qdrant/bm25")
        except Exception as e:
            print(f"Failed to set FastEmbed models: {e}")
            
    return _qdrant_client

def retrieve(query: str, collection_name: str, k: int = 4, filter_dict: dict = None, index_dir: str = "data/qdrant_index"):
    """
    Search the vector store for the most relevant documents using Hybrid Search + Reranking.
    """
    client = get_qdrant_client(index_dir)
    
    qdrant_filter = None
    if filter_dict:
        conditions = []
        for key, value in filter_dict.items():
            conditions.append(
                models.FieldCondition(
                    key=key,
                    match=models.MatchValue(value=value)
                )
            )
        qdrant_filter = models.Filter(must=conditions)
        
    try:
        # Native Hybrid Search
        results = client.query(
            collection_name=collection_name,
            query_text=query,
            query_filter=qdrant_filter,
            limit=k * 2 # Fetch 2x for reranking
        )
    except Exception as e:
        print(f"Error querying Qdrant natively: {e}")
        return []
        
    lc_docs = []
    for point in results:
        payload = point.metadata if hasattr(point, "metadata") else getattr(point, "payload", {})
        doc_content = getattr(point, "document", None)
        if not doc_content:
            doc_content = payload.get("page_content", "")
            
        lc_docs.append(LcDoc(page_content=doc_content, metadata=payload))
        
    if not lc_docs:
        return []
        
    try:
        reranker = get_reranker()
        reranked_docs = reranker.compress_documents(documents=lc_docs, query=query)
        return reranked_docs[:k]
    except Exception as e:
        print(f"Reranking error: {e}")
        return lc_docs[:k]

