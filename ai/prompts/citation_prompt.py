from langchain_core.prompts import PromptTemplate

CITATION_PROMPT = PromptTemplate(
    template="""
    You are an expert Legal Researcher. Identify any citations, source documents, 
    statutes, or precedents mentioned in the context. Format them as proper citations.
    Set 'verified' to true if they are explicitly mentioned in the text.
    
    Query: {query}
    
    Context:
    {context}
    """,
    input_variables=["query", "context"]
)
