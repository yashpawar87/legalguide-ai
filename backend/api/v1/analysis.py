from fastapi import APIRouter, HTTPException, Depends
from backend.schemas.analysis import AnalysisRequest, AnalysisResponse
from backend.api.v1.auth import verify_token
from ai.graph.legal_graph import create_legal_graph
from sqlalchemy.orm import Session
from backend.db.deps import get_db
from backend.model.document import Document
from backend.model.chat import ChatSession, ChatMessage
from langchain_core.messages import HumanMessage, AIMessage
import traceback

router = APIRouter(tags=["Analysis"])

# Initialize LangGraph once at startup
legal_app = create_legal_graph()

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_query(
    request: AnalysisRequest, 
    user: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """
    Accepts a legal query, runs it through the LangGraph multi-agent workflow,
    and returns a structured response containing the final report, statutes, and precedents.
    """
    try:
        if request.document_id:
            # Defense in depth: Verify document ownership in PostgreSQL
            try:
                doc_id = int(request.document_id)
                doc = db.query(Document).filter(Document.id == doc_id).first()
                if not doc:
                    raise HTTPException(status_code=404, detail="Document not found.")
                if doc.user_id != user["uid"]:
                    raise HTTPException(status_code=403, detail="Access denied to this document.")
            except ValueError:
                pass # Ignore if it's not an integer (e.g., fallback strings)

        messages_list = []
        if request.session_id:
            session = db.query(ChatSession).filter(ChatSession.id == request.session_id, ChatSession.user_id == user["uid"]).first()
            if not session:
                raise HTTPException(status_code=404, detail="Chat session not found.")
            
            # Fetch past messages to inject context
            past_msgs = db.query(ChatMessage).filter(ChatMessage.session_id == request.session_id).order_by(ChatMessage.created_at.asc()).all()
            for m in past_msgs:
                if m.role == "user":
                    messages_list.append(HumanMessage(content=m.content))
                else:
                    messages_list.append(AIMessage(content=m.content))

            user_msg = ChatMessage(session_id=request.session_id, role="user", content=request.query)
            db.add(user_msg)
            db.commit()

        initial_state = {
            "query": request.query,
            "query_intent": "",
            "document_id": request.document_id or "",
            "user_id": user["uid"],
            "user_document_context": "",
            "retrieved_docs": [],
            "context": "",
            "context_bnss": "",
            "context_ipc": "",
            "context_qna": "",
            "context_precedents": "",
            "statutes": [],
            "precedents": [],
            "risks": [],
            "analysis": "",
            "citations": [],
            "final_report": "",
            "error": None,
            "metadata": {},
            "messages": messages_list
        }
        
        # Invoke the multi-agent graph
        final_state = legal_app.invoke(initial_state)
        
        # Check if the graph yielded an error
        if final_state.get("error"):
            raise HTTPException(status_code=500, detail=final_state["error"])
            
        final_report = final_state.get("final_report", "No report generated.")

        if request.session_id:
            ai_msg = ChatMessage(session_id=request.session_id, role="ai", content=final_report)
            db.add(ai_msg)
            db.commit()

        # Map state back to response schema
        return AnalysisResponse(
            query=final_state["query"],
            final_report=final_report,
            statutes=[dict(s) for s in final_state.get("statutes", [])],
            precedents=[dict(p) for p in final_state.get("precedents", [])],
            risks=[dict(r) for r in final_state.get("risks", [])],
            citations=[dict(c) for c in final_state.get("citations", [])]
        )
        
    except Exception as e:
        print(f"Error executing LangGraph: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))
