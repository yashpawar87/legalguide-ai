import os
from langchain_qdrant import Qdrant
from qdrant_client import QdrantClient
from ai.embeddings.embedding_model import get_embedding_model

_vector_stores = {}
_qdrant_client = None

def get_qdrant_client(index_dir: str = "data/qdrant_index"):
    global _qdrant_client
    if _qdrant_client is None:
        if os.path.exists(index_dir):
            _qdrant_client = QdrantClient(path=index_dir)
        else:
            # Create a new local DB if it doesn't exist
            _qdrant_client = QdrantClient(path=index_dir)
    return _qdrant_client

def load_vector_store(collection_name: str, index_dir: str = "data/qdrant_index"):
    """
    Loads the Qdrant index from disk. Uses a global variable to cache it 
    so it isn't reloaded on every search request.
    """
    global _vector_stores, _qdrant_client
    if collection_name in _vector_stores:
        return _vector_stores[collection_name]
        
    if os.path.exists(index_dir):
        embeddings = get_embedding_model()
        try:
            client = get_qdrant_client(index_dir)
            _vector_stores[collection_name] = Qdrant(
                client=client,
                collection_name=collection_name,
                embeddings=embeddings,
            )
            print(f"Loaded Qdrant index from '{index_dir}' for collection '{collection_name}'")
        except Exception as e:
            print(f"Error loading Qdrant index: {e}")
    else:
        print(f"Warning: No Qdrant index found at '{index_dir}'. Please run ingestion first.")
        
    return _vector_stores.get(collection_name)

def retrieve(query: str, collection_name: str, k: int = 4, filter_dict: dict = None, index_dir: str = "data/qdrant_index"):
    """
    Search the vector store for the most relevant documents.
    
    :param query: The search query string.
    :param collection_name: The Qdrant collection to search in.
    :param k: The number of results to return (default 4).
    :param filter_dict: Optional metadata filter (e.g., {"court_name": "Supreme Court"}).
    :param index_dir: Directory where the Qdrant index is stored.
    :return: A list of Langchain Document objects.
    """
    vector_store = load_vector_store(collection_name, index_dir)
    
    if not vector_store:
        raise ValueError("Vector store is not loaded. Cannot perform search. Please ingest data first.")
        
    kwargs = {"k": k}
    if filter_dict:
        # Langchain Qdrant supports filtering via the 'filter' kwarg
        kwargs["filter"] = filter_dict
        
    results = vector_store.similarity_search(query, **kwargs)
    return results

