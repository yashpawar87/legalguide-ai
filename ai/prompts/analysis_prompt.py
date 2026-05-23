from langchain_core.prompts import PromptTemplate

ANALYSIS_PROMPT = PromptTemplate(
    template="""
    You are an expert Legal Counsel. Perform a deep reasoning analysis to answer the user's query.
    IMPORTANT: If there is context from a user-uploaded document, treat those facts as the absolute Ground Truth. 
    Use the rest of the legal corpus (BNSS, IPC, Precedents) to provide the legal framework around those facts.
    
    Query: {query}
    
    Context:
    {context}
    
    Analysis:
    """,
    input_variables=["query", "context"]
)
