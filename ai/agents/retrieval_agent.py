from ai.graph.state import LegalGraphState
from ai.rag.retriever import retrieve

def retrieval_node(state: LegalGraphState) -> dict:
    """
    Node 1: Retrieval Agent
    Takes the user query, performs a FAISS vector search, and formats the context.
    """
    print("--- [Node] Retrieval Agent ---")
    query = state.get("query", "")
    document_id = state.get("document_id", "")
    user_id = state.get("user_id", "")
    
    if not query:
        return {"error": "Empty query provided to retrieval node."}

    try:
        from langchain_core.documents import Document as LcDoc
        user_docs = []
        if document_id:
            try:
                # Qdrant requires specific models for payload filtering. Langchain wrapper uses dictionary filters.
                filter_dict = {"document_id": int(document_id), "user_id": user_id} 
                user_docs = retrieve(query, collection_name="user_documents_collection", k=5, filter_dict=filter_dict)
            except Exception as e:
                print(f"Warning: Failed to retrieve user document: {e}")
                
        bnss_docs = retrieve(query, collection_name="bnss_collection", k=3)
        ipc_docs = retrieve(query, collection_name="ipc_collection", k=3)
        qna_docs = retrieve(query, collection_name="constitution_collection", k=3)
        precedent_docs = retrieve(query, collection_name="precedents_collection", k=5)
    except Exception as e:
        return {"error": f"Retrieval failed: {e}"}

    # Format into clean strings for the LLM context
    def format_docs(docs):
        ctx = ""
        for i, doc in enumerate(docs):
            source = doc.metadata.get('source_file', doc.metadata.get('act_name', doc.metadata.get('source', 'Unknown')))
            page = doc.metadata.get('page_num', doc.metadata.get('section_no', ''))
            ctx += f"\n[Source: {source} | Ref: {page}]\n{doc.page_content}\n"
        return ctx.strip()

    context_user = format_docs(user_docs)
    context_bnss = format_docs(bnss_docs)
    context_ipc = format_docs(ipc_docs)
    context_qna = format_docs(qna_docs)
    context_precedents = format_docs(precedent_docs)
    
    # Combined general context
    combined_docs = user_docs + bnss_docs + ipc_docs + qna_docs + precedent_docs
    context_str = context_user + "\n\n" + context_bnss + "\n\n" + context_ipc + "\n\n" + context_qna + "\n\n" + context_precedents
        
    return {
        "retrieved_docs": combined_docs,
        "user_document_context": context_user,
        "context_bnss": context_bnss,
        "context_ipc": context_ipc,
        "context_qna": context_qna,
        "context_precedents": context_precedents,
        "context": context_str.strip()
    }
