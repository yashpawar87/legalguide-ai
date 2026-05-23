from langchain_core.prompts import PromptTemplate

RISK_PROMPT = PromptTemplate(
    template="""
    You are an expert Legal Risk Analyst. Analyze the context and query to identify 
    any legal risks, vulnerabilities, or red flags. Classify severity as High, Medium, or Low.
    
    Query: {query}
    
    Context:
    {context}
    """,
    input_variables=["query", "context"]
)
