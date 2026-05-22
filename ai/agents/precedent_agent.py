from backend.config import settings
from ai.config import get_fast_llm
from pydantic import BaseModel
from typing import List
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from ai.graph.state import LegalGraphState, Precedent

class PrecedentOutput(BaseModel):
    precedents: List[Precedent]

def precedent_node(state: LegalGraphState) -> dict:
    print("--- [Node] Precedent Agent ---")
    context = state.get("context", "")
    query = state.get("query", "")
    
    if not context:
        return {"precedents": []}
        
    llm = get_fast_llm()
    structured_llm = llm.with_structured_output(PrecedentOutput)
    
    prompt = PromptTemplate(
        template="""
        You are an expert Legal AI. Extract any similar case precedents, past judgments, 
        or legal principles cited in the context.
        
        Query: {query}
        
        Context:
        {context}
        """,
        input_variables=["query", "context"]
    )
    
    chain = prompt | structured_llm
    try:
        result = chain.invoke({"query": query, "context": context})
        return {"precedents": result.get("precedents", []) if isinstance(result, dict) else getattr(result, "precedents", [])}
    except Exception as e:
        print(f"Precedent Agent Error: {e}")
        return {"precedents": []}
