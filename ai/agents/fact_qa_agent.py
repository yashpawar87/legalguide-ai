from ai.graph.state import LegalGraphState
from ai.config import get_heavy_llm
from ai.rag.retriever import retrieve
from langchain_core.prompts import PromptTemplate

FACT_QA_PROMPT = PromptTemplate(
    template="""
    You are an expert Document Analyst. Answer the user's question directly and concisely 
    using ONLY the provided document context.
    
    If the context does not contain the answer, say "I cannot find the answer in the uploaded document."
    Do NOT invent facts, and do NOT provide generic legal advice.
    
    Context from Document:
    {context}
    
    Question: {query}
    
    Direct Answer:
    """,
    input_variables=["context", "query"]
)

def fact_qa_node(state: LegalGraphState) -> dict:
    """
    Node: Fact QA Fast-Track
    Retrieves only from the user's uploaded document and provides a direct answer,
    skipping all other legal reasoning agents.
    """
    print("--- [Node] Fact QA Agent (Fast Track) ---")
    query = state.get("query", "")
    document_id = state.get("document_id", "")
    
    if not document_id:
        return {
            "final_report": "This query was routed as factual, but no document was uploaded. Please upload a document first or ask a legal question.",
            "statutes": [], "precedents": [], "risks": [], "citations": []
        }
        
    try:
        filter_dict = {"document_id": int(document_id)}
        user_docs = retrieve(query, collection_name="user_documents_collection", k=5, filter_dict=filter_dict)
        
        context_str = "\n".join([doc.page_content for doc in user_docs]).strip()
        
        if not context_str:
            return {
                "final_report": "I could not find any relevant information in the uploaded document regarding your question.",
                "statutes": [], "precedents": [], "risks": [], "citations": []
            }
            
        llm = get_heavy_llm()
        chain = FACT_QA_PROMPT | llm
        result = chain.invoke({"query": query, "context": context_str})
        
        # Directly format the output for the Streamlit UI to render as the final report
        return {
            "final_report": result.content,
            "statutes": [], # Empty because we skipped legal reasoning
            "precedents": [],
            "risks": [],
            "citations": [{"source_type": "Uploaded Document", "reference": "User Document", "verified": True}]
        }
        
    except Exception as e:
        print(f"Fact QA Error: {e}")
        return {"error": f"Failed to retrieve facts from document: {e}"}
