from backend.config import settings
from ai.config import get_fast_llm
from pydantic import BaseModel
from typing import List
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from ai.prompts.precedent_prompt import PRECEDENT_PROMPT
from ai.graph.state import LegalGraphState, Precedent

class PrecedentOutput(BaseModel):
    precedents: List[Precedent]

def precedent_node(state: LegalGraphState) -> dict:
    print("--- [Node] Precedent Agent ---")
    context_precedents = state.get("context_precedents", "")
    user_document_context = state.get("user_document_context", "")
    query = state.get("query", "")
    statutes = state.get("statutes", [])
    
    if not query:
        return {"precedents": []}
        
    llm = get_fast_llm()
    structured_llm = llm.with_structured_output(PrecedentOutput)
    
    chain = PRECEDENT_PROMPT | structured_llm
    
    # Format statutes as a readable string
    statutes_str = "\n".join([f"{s.act_name} Section {s.section}: {s.relevance}" for s in statutes])
    
    try:
        result = chain.invoke({
            "query": query, 
            "user_document_context": user_document_context,
            "statutes": statutes_str,
            "context_precedents": context_precedents
        })
        return {"precedents": result.get("precedents", []) if isinstance(result, dict) else getattr(result, "precedents", [])}
    except Exception as e:
        print(f"Precedent Agent Error: {e}")
        return {"precedents": []}
