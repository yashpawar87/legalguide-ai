from typing import TypedDict, Annotated, Sequence, List, Optional, Dict, Any
import operator
from langchain_core.messages import BaseMessage
from langchain.schema import Document
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Structured Output Schemas (Used by specific agents to format their output)
# ---------------------------------------------------------------------------

class Statute(BaseModel):
    act_name: str
    section: str
    relevance: str

class Precedent(BaseModel):
    case_name: str
    citation: str
    legal_principle: str
    relevance: str

class Risk(BaseModel):
    risk_category: str
    description: str
    severity: str # e.g., High, Medium, Low

class Citation(BaseModel):
    source_type: str # e.g., Statute, Precedent, Document
    reference: str
    verified: bool

# ---------------------------------------------------------------------------
# Global Graph State Schema
# ---------------------------------------------------------------------------

class LegalGraphState(TypedDict):
    """
    LegalGuideAI LangGraph State Graph
    This state flows through all nodes with conditional routing.
    Each agent reads from and writes back to this single source of truth.
    """
    
    query: str                          # Original user query
    query_intent: str                   # 'factual' or 'legal'
    document_id: str                    # Uploaded document ID
    user_id: str                        # Authenticated User ID
    user_document_context: str          # Formatted context from uploaded doc
    retrieved_docs: List[Document]      # Retrieved context from FAISS
    context_bnss: str                   # Formatted context from BNSS
    context_ipc: str                    # Formatted context from IPC
    context_precedents: str             # Formatted context from precedents
    context_qna: str                    # Formatted context from Constitution/QA
    context: str                        # General context (kept for fallback)
    statutes: List[Statute]             # Applicable laws
    precedents: List[Precedent]         # Similar case precedents
    risks: List[Risk]                   # Identified risks
    analysis: str                       # Legal analysis
    citations: List[Citation]           # All citations
    final_report: str                   # Final synthesized report
    error: Optional[str]                # Error message if any
    metadata: Dict[str, Any]            # Additional metadata
    
    # Keeps a log of the LangGraph node messages for debugging/tracing
    messages: Annotated[Sequence[BaseMessage], operator.add]
