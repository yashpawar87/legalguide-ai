from backend.config import settings
from ai.config import get_heavy_llm
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from ai.prompts.synthesis_prompt import SYNTHESIS_PROMPT
from ai.graph.state import LegalGraphState

def synthesis_node(state: LegalGraphState) -> dict:
    print("--- [Node] Synthesis Agent ---")
    
    query = state.get("query", "")
    analysis = state.get("analysis", "")
    statutes = state.get("statutes", [])
    precedents = state.get("precedents", [])
    risks = state.get("risks", [])
    citations = state.get("citations", [])
    
    # Format the lists into readable strings
    statutes_str = "\n".join([f"- {s.act_name}, Sec {s.section}: {s.relevance}" for s in statutes])
    precedents_str = "\n".join([f"- {p.case_name} ({p.citation}): {p.legal_principle}" for p in precedents])
    risks_str = "\n".join([f"- [{r.severity}] {r.risk_category}: {r.description}" for r in risks])
    citations_str = "\n".join([f"- {c.source_type}: {c.reference}" for c in citations])
    
    llm = get_heavy_llm()
    
    chain = SYNTHESIS_PROMPT | llm
    try:
        result = chain.invoke({
            "query": query,
            "analysis": analysis,
            "statutes_str": statutes_str,
            "precedents_str": precedents_str,
            "risks_str": risks_str,
            "citations_str": citations_str
        })
        return {"final_report": result.content}
    except Exception as e:
        print(f"Synthesis Agent Error: {e}")
        return {"final_report": "Error generating final synthesis report."}
