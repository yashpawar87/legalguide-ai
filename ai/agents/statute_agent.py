from backend.config import settings
from ai.config import get_fast_llm
from pydantic import BaseModel
from typing import List
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from ai.prompts.statute_prompt import STATUTE_PROMPT
from ai.graph.state import LegalGraphState, Statute

class StatuteOutput(BaseModel):
    statutes: List[Statute]

def statute_node(state: LegalGraphState) -> dict:
    print("--- [Node] Statute Agent ---")
    context_bnss = state.get("context_bnss", "")
    context_ipc = state.get("context_ipc", "")
    context_qna = state.get("context_qna", "")
    user_document_context = state.get("user_document_context", "")
    query = state.get("query", "")
    
    if not query:
        return {"statutes": []}
        
    llm = get_fast_llm()
    structured_llm = llm.with_structured_output(StatuteOutput)
    
    chain = STATUTE_PROMPT | structured_llm
    try:
        result = chain.invoke({
            "query": query, 
            "user_document_context": user_document_context,
            "context_bnss": context_bnss,
            "context_ipc": context_ipc,
            "context_qna": context_qna
        })
        return {"statutes": result.get("statutes", []) if isinstance(result, dict) else getattr(result, "statutes", [])}
    except Exception as e:
        print(f"Statute Agent Error: {e}")
        return {"statutes": []}
