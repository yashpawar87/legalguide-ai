from langchain_core.prompts import PromptTemplate

STATUTE_PROMPT = PromptTemplate(
    template="""
    You are an expert Legal AI. Extract applicable laws, statutes, acts, or sections 
    mentioned or highly relevant to the query based ONLY on the provided legal references.
    
    IMPORTANT: If a User Uploaded Document Context is provided, those facts are Ground Truth.
    Ensure that the statutes you recommend strictly apply to those specific facts.
    
    Query: {query}
    
    User Uploaded Document Context:
    {user_document_context}
    
    BNSS (Procedural Laws) Context:
    {context_bnss}
    
    IPC (Penal Code) Context:
    {context_ipc}
    
    Constitution Context:
    {context_qna}
    """,
    input_variables=["query", "user_document_context", "context_bnss", "context_ipc", "context_qna"]
)
