from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class StatuteSchema(BaseModel):
    act_name: str
    section: str
    relevance: str

class PrecedentSchema(BaseModel):
    case_name: str
    citation: str
    legal_principle: str
    relevance: str

class RiskSchema(BaseModel):
    risk_category: str
    description: str
    severity: str

class CitationSchema(BaseModel):
    source_type: str
    reference: str
    verified: bool

class AnalysisRequest(BaseModel):
    query: str
    document_id: Optional[str] = None
    session_id: Optional[int] = None
    
class AnalysisResponse(BaseModel):
    query: str
    final_report: str
    statutes: List[StatuteSchema]
    precedents: List[PrecedentSchema]
    risks: List[RiskSchema]
    citations: List[CitationSchema]
