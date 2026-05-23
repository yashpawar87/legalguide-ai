from backend.config import settings
from ai.config import get_heavy_llm
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from ai.prompts.analysis_prompt import ANALYSIS_PROMPT
from ai.graph.state import LegalGraphState

def analysis_node(state: LegalGraphState) -> dict:
    print("--- [Node] Analysis Agent ---")
    context = state.get("context", "")
    query = state.get("query", "")
    
    if not context:
        return {"analysis": "No context available for analysis."}
        
    llm = get_heavy_llm()
    
    chain = ANALYSIS_PROMPT | llm
    try:
        result = chain.invoke({"query": query, "context": context})
        return {"analysis": result.content}
    except Exception as e:
        print(f"Analysis Agent Error: {e}")
        return {"analysis": "Error during analysis."}
