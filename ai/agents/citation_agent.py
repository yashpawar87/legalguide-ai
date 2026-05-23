from backend.config import settings
from ai.config import get_fast_llm
from pydantic import BaseModel
from typing import List
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from ai.prompts.citation_prompt import CITATION_PROMPT
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
    
    chain = CITATION_PROMPT | structured_llm
    try:
        result = chain.invoke({"query": query, "context": context})
        return {"citations": result.get("citations", []) if isinstance(result, dict) else getattr(result, "citations", [])}
    except Exception as e:
        print(f"Citation Agent Error: {e}")
        return {"citations": []}
