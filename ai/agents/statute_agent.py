from backend.config import settings
from ai.config import get_fast_llm
from pydantic import BaseModel
from typing import List
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from ai.graph.state import LegalGraphState, Statute

class StatuteOutput(BaseModel):
    statutes: List[Statute]

def statute_node(state: LegalGraphState) -> dict:
    print("--- [Node] Statute Agent ---")
    context = state.get("context", "")
    query = state.get("query", "")
    
    if not context:
        return {"statutes": []}
        
    llm = get_fast_llm()
    structured_llm = llm.with_structured_output(StatuteOutput)
    
    prompt = PromptTemplate(
        template="""
        You are an expert Legal AI. Extract applicable laws, statutes, acts, or sections 
        mentioned or highly relevant to the context and query.
        
        Query: {query}
        
        Context:
        {context}
        """,
        input_variables=["query", "context"]
    )
    
    chain = prompt | structured_llm
    try:
        result = chain.invoke({"query": query, "context": context})
        return {"statutes": result.get("statutes", []) if isinstance(result, dict) else getattr(result, "statutes", [])}
    except Exception as e:
        print(f"Statute Agent Error: {e}")
        return {"statutes": []}
