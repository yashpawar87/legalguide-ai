import requests
import streamlit as st
import logging

API_BASE_URL = "http://127.0.0.1:8000/api/v1"

def analyze_query(query: str, document_id: str = None, session_id: int = None) -> dict:
    """
    Sends a legal query to the FastAPI analysis endpoint.
    Returns the structured JSON response containing the final report, 
    statutes, precedents, risks, and citations.
    """
    url = f"{API_BASE_URL}/analysis/analyze"
    payload = {
        "query": query,
        "document_id": document_id,
        "session_id": session_id
    }
    
    headers = {}
    if "id_token" in st.session_state and st.session_state.id_token:
        headers["Authorization"] = f"Bearer {st.session_state.id_token}"
        
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=120)  # Extended timeout for LLM inference
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        logging.error("Analysis request timed out.")
        return {"error": "The analysis request timed out. Please try a simpler query."}
    except requests.exceptions.RequestException as e:
        logging.error(f"Analysis API error: {e}")
        error_detail = "Failed to communicate with the AI backend."
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_data = e.response.json()
                if "detail" in error_data:
                    error_detail = error_data["detail"]
            except Exception:
                pass
        return {"error": error_detail}

def upload_document(file_bytes: bytes, filename: str) -> dict:
    """
    Uploads a document to the FastAPI document endpoint.
    Currently a placeholder until the document router is fully built out.
    """
    url = f"{API_BASE_URL}/documents/upload"
    files = {"file": (filename, file_bytes)}
    headers = {}
    if "id_token" in st.session_state and st.session_state.id_token:
        headers["Authorization"] = f"Bearer {st.session_state.id_token}"
        
    try:
        response = requests.post(url, files=files, headers=headers, timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Upload API error: {e}")
        return {"error": "Failed to upload document."}

def get_chat_sessions() -> list:
    url = f"{API_BASE_URL}/chats/sessions"
    headers = {}
    if "id_token" in st.session_state and st.session_state.id_token:
        headers["Authorization"] = f"Bearer {st.session_state.id_token}"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except:
        return []

def create_chat_session(title: str) -> dict:
    url = f"{API_BASE_URL}/chats/sessions"
    payload = {"title": title}
    headers = {}
    if "id_token" in st.session_state and st.session_state.id_token:
        headers["Authorization"] = f"Bearer {st.session_state.id_token}"
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def get_chat_messages(session_id: int) -> list:
    url = f"{API_BASE_URL}/chats/sessions/{session_id}/messages"
    headers = {}
    if "id_token" in st.session_state and st.session_state.id_token:
        headers["Authorization"] = f"Bearer {st.session_state.id_token}"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except:
        return []
