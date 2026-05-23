from langchain_core.prompts import PromptTemplate

PRECEDENT_PROMPT = PromptTemplate(
    template="""
    You are an expert Legal AI. Extract any similar case precedents, past judgments, 
    or legal principles cited in the provided legal precedent context that are highly 
    relevant to the user's query and the applicable statutes.
    
    IMPORTANT: If a User Uploaded Document Context is provided, those facts are Ground Truth.
    Ensure that the precedents you recommend are factually analogous to the uploaded document.
    
    Query: {query}
    
    User Uploaded Document Context:
    {user_document_context}
    
    Applicable Statutes:
    {statutes}
    
    Precedent Context:
    {context_precedents}
    """,
    input_variables=["query", "user_document_context", "statutes", "context_precedents"]
)
