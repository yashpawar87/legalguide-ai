from backend.config import settings
from ai.config import get_fast_llm
from pydantic import BaseModel
from typing import List
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from ai.graph.state import LegalGraphState, Citation

class CitationOutput(BaseModel):
    citations: List[Citation]

def citation_node(state: LegalGraphState) -> dict:
    print("--- [Node] Citation Agent ---")
    context = state.get("context", "")
    query = state.get("query", "")
    
    if not context:
        return {"citations": []}
        
    llm = get_fast_llm()
    structured_llm = llm.with_structured_output(CitationOutput)
    
    prompt = PromptTemplate(
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
    
    chain = prompt | structured_llm
    try:
        result = chain.invoke({"query": query, "context": context})
        return {"citations": result.get("citations", []) if isinstance(result, dict) else getattr(result, "citations", [])}
    except Exception as e:
        print(f"Citation Agent Error: {e}")
        return {"citations": []}
