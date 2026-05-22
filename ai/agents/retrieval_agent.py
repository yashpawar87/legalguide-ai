from ai.graph.state import LegalGraphState
from ai.rag.retriever import retrieve

def retrieval_node(state: LegalGraphState) -> dict:
    """
    Node 1: Retrieval Agent
    Takes the user query, performs a FAISS vector search, and formats the context.
    """
    print("--- [Node] Retrieval Agent ---")
    query = state.get("query", "")
    
    if not query:
        return {"error": "Empty query provided to retrieval node."}

    # Retrieve top 5 most relevant document chunks
    try:
        retrieved_docs = retrieve(query, k=5)
    except Exception as e:
        return {"error": f"Retrieval failed: {e}"}

    # Format into a clean string for the LLM context
    context_str = ""
    for i, doc in enumerate(retrieved_docs):
        page = doc.metadata.get('page_num', 'Unknown')
        source = doc.metadata.get('source', 'Unknown')
        context_str += f"\n[Source: {source} | Page: {page}]\n{doc.page_content}\n"
        
    return {
        "retrieved_docs": retrieved_docs,
        "context": context_str.strip()
    }
