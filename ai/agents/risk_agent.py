from backend.config import settings
from ai.config import get_fast_llm
from pydantic import BaseModel
from typing import List
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from ai.prompts.risk_prompt import RISK_PROMPT
from ai.graph.state import LegalGraphState, Risk

class RiskOutput(BaseModel):
    risks: List[Risk]

def risk_node(state: LegalGraphState) -> dict:
    print("--- [Node] Risk Agent ---")
    context = state.get("context", "")
    query = state.get("query", "")
    
    if not context:
        return {"risks": []}
        
    llm = get_fast_llm()
    structured_llm = llm.with_structured_output(RiskOutput)
    
    chain = RISK_PROMPT | structured_llm
    try:
        result = chain.invoke({"query": query, "context": context})
        return {"risks": result.get("risks", []) if isinstance(result, dict) else getattr(result, "risks", [])}
    except Exception as e:
        print(f"Risk Agent Error: {e}")
        return {"risks": []}
