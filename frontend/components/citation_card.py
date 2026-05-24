import streamlit as st

def render_statute(statute: dict):
    """
    Renders a styled card for a statute.
    """
    act_name = statute.get("act_name", "Unknown Act")
    section = statute.get("section", "Unknown Section")
    relevance = statute.get("relevance", "No relevance provided.")
    
    html = f"""
    <div style="
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-left: 4px solid #4F46E5;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    ">
        <h4 style="margin-top: 0; color: #E5E7EB;">📜 {act_name} - Section {section}</h4>
        <p style="color: #9CA3AF; font-size: 0.95em; margin-bottom: 0;">{relevance}</p>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_precedent(precedent: dict):
    """
    Renders a styled card for a legal precedent.
    """
    case_name = precedent.get("case_name", "Unknown Case")
    citation = precedent.get("citation", "No Citation")
    principle = precedent.get("legal_principle", "No principle provided.")
    relevance = precedent.get("relevance", "No relevance provided.")
    
    html = f"""
    <div style="
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-left: 4px solid #10B981;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    ">
        <h4 style="margin-top: 0; color: #E5E7EB;">⚖️ {case_name}</h4>
        <p style="color: #6EE7B7; font-size: 0.85em; font-weight: bold; margin-bottom: 8px;">{citation}</p>
        <p style="color: #9CA3AF; font-size: 0.95em; margin-bottom: 8px;"><strong>Principle:</strong> {principle}</p>
        <p style="color: #9CA3AF; font-size: 0.95em; margin-bottom: 0;"><strong>Relevance:</strong> {relevance}</p>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
