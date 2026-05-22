import os
from langchain_qdrant import Qdrant
from qdrant_client import QdrantClient
from ai.embeddings.embedding_model import get_embedding_model

_vector_store = None

def load_vector_store(index_dir: str = "data/qdrant_index"):
    """
    Loads the Qdrant index from disk. Uses a global variable to cache it 
    so it isn't reloaded on every search request.
    """
    global _vector_store
    if _vector_store is not None:
        return _vector_store
        
    if os.path.exists(index_dir):
        embeddings = get_embedding_model()
        try:
            client = QdrantClient(path=index_dir)
            _vector_store = Qdrant(
                client=client,
                collection_name="legal_docs",
                embeddings=embeddings,
            )
            print(f"Loaded Qdrant index from '{index_dir}'")
        except Exception as e:
            print(f"Error loading Qdrant index: {e}")
    else:
        print(f"Warning: No Qdrant index found at '{index_dir}'. Please run ingestion first.")
        
    return _vector_store

def retrieve(query: str, k: int = 4, filter_dict: dict = None, index_dir: str = "data/qdrant_index"):
    """
    Search the vector store for the most relevant documents.
    
    :param query: The search query string.
    :param k: The number of results to return (default 4).
    :param filter_dict: Optional metadata filter (e.g., {"court_name": "Supreme Court"}).
    :param index_dir: Directory where the Qdrant index is stored.
    :return: A list of Langchain Document objects.
    """
    vector_store = load_vector_store(index_dir)
    
    if not vector_store:
        raise ValueError("Vector store is not loaded. Cannot perform search. Please ingest data first.")
        
    kwargs = {"k": k}
    if filter_dict:
        # Langchain Qdrant supports filtering via the 'filter' kwarg
        kwargs["filter"] = filter_dict
        
    results = vector_store.similarity_search(query, **kwargs)
    return results

