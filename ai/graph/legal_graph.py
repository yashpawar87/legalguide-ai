from langgraph.graph import StateGraph, START, END
from ai.graph.state import LegalGraphState

# Import all agents
from ai.agents.retrieval_agent import retrieval_node
from ai.agents.statute_agent import statute_node
from ai.agents.precedent_agent import precedent_node
from ai.agents.risk_agent import risk_node
from ai.agents.analysis_agent import analysis_node
from ai.agents.citation_agent import citation_node
from ai.agents.synthesis_agent import synthesis_node
from ai.agents.router_agent import router_node
from ai.agents.fact_qa_agent import fact_qa_node

def route_query(state: LegalGraphState):
    """Conditional routing logic based on intent classification."""
    intent = state.get("query_intent", "legal")
    if intent == "factual":
        return "FactQAAgent"
    return "RetrievalAgent"

def create_legal_graph():
    """
    Creates and compiles the LegalGuide AI multi-agent LangGraph workflow.
    """
    # Initialize the graph with the global state schema
    workflow = StateGraph(LegalGraphState)
    
    workflow.add_node("RouterAgent", router_node)
    workflow.add_node("FactQAAgent", fact_qa_node)
    workflow.add_node("RetrievalAgent", retrieval_node)
    workflow.add_node("StatuteAgent", statute_node)
    workflow.add_node("PrecedentAgent", precedent_node)
    workflow.add_node("RiskAgent", risk_node)
    workflow.add_node("AnalysisAgent", analysis_node)
    workflow.add_node("CitationAgent", citation_node)
    workflow.add_node("SynthesisAgent", synthesis_node)
    
    # 2. Define the edges (workflow routing)
    
    # Step 1: Start at Router
    workflow.add_edge(START, "RouterAgent")
    
    # Step 2: Conditional Routing based on Intent
    workflow.add_conditional_edges(
        "RouterAgent",
        route_query
    )
    
    # Fast-Track Path: Fact QA immediately ends
    workflow.add_edge("FactQAAgent", END)
    
    # Step 2: Extract Statutes based on retrieved context
    workflow.add_edge("RetrievalAgent", "StatuteAgent")
    
    # Step 3: Fan-out (Parallel Execution) 
    # Statute Agent branches to specialized analysis agents
    workflow.add_edge("StatuteAgent", "PrecedentAgent")
    workflow.add_edge("StatuteAgent", "RiskAgent")
    workflow.add_edge("StatuteAgent", "AnalysisAgent")
    workflow.add_edge("StatuteAgent", "CitationAgent")
    
    # Step 4: Fan-in (Convergence)
    # All specialized agents feed their findings into the Synthesis Agent
    workflow.add_edge("PrecedentAgent", "SynthesisAgent")
    workflow.add_edge("RiskAgent", "SynthesisAgent")
    workflow.add_edge("AnalysisAgent", "SynthesisAgent")
    workflow.add_edge("CitationAgent", "SynthesisAgent")
    
    # Step 5: End
    workflow.add_edge("SynthesisAgent", END)
    
    # Compile the graph into an executable application
    app = workflow.compile()
    
    return app
