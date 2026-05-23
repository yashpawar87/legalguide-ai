from ai.graph.state import LegalGraphState
from ai.config import get_fast_llm
from langchain_core.prompts import PromptTemplate

ROUTER_PROMPT = PromptTemplate(
    template="""
    You are an expert Legal Assistant routing user queries.
    Analyze the user's query and determine if it is asking for a simple FACT from a document, or if it is asking for LEGAL REASONING.
    
    If the user asks: "What color was the car?", "What was stolen?", "What date was mentioned?" -> Output EXACTLY: factual
    If the user asks: "What legal remedies are available?", "What sections apply?", "Is this a crime?" -> Output EXACTLY: legal
    
    Query: {query}
    
    Output ONLY 'factual' or 'legal'. Nothing else.
    """,
    input_variables=["query"]
)

def router_node(state: LegalGraphState) -> dict:
    """
    Node 0: Router Agent
    Determines if the query is factual or requires deep legal reasoning.
    """
    print("--- [Node] Router Agent ---")
    query = state.get("query", "")
    
    if not query:
        return {"query_intent": "legal"} # Default to legal pipeline
        
    llm = get_fast_llm()
    chain = ROUTER_PROMPT | llm
    
    try:
        result = chain.invoke({"query": query})
        intent = result.content.strip().lower()
        
        # Fallback safety
        if intent not in ["factual", "legal"]:
            intent = "legal"
            
        print(f"   Intent Classified: {intent.upper()}")
        return {"query_intent": intent}
        
    except Exception as e:
        print(f"Router Error: {e}")
        return {"query_intent": "legal"} # Safe fallback
