import streamlit as st
from utils.api_client import get_chat_sessions, get_chat_messages

def render_sidebar():
    """
    Renders the custom sidebar with app information, history placeholders, and settings.
    """
    with st.sidebar:
        st.markdown(
            """
            <div style='text-align: center; padding-bottom: 20px;'>
                <h2 style='color: #4F46E5; margin-bottom: 0;'>LegalGuide AI</h2>
                <p style='color: #6B7280; font-size: 0.9em; margin-top: 0;'>Legal Intelligence Platform</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        if st.button("➕ New Conversation", use_container_width=True):
            st.session_state.messages = []
            st.session_state.current_session_id = None
            st.rerun()
            
        st.markdown("---")
        
        st.markdown("### 🕒 Chat History")
        sessions = get_chat_sessions()
        if not sessions:
            st.caption("No past conversations.")
        else:
            for s in sessions:
                if st.button(f"📝 {s['title'][:30]}", use_container_width=True, key=f"hist_{s['id']}"):
                    st.session_state.current_session_id = s["id"]
                    msgs = get_chat_messages(s["id"])
                    st.session_state.messages = []
                    for m in msgs:
                        if m["role"] == "user":
                            st.session_state.messages.append({"role": "user", "content": m["content"]})
                        else:
                            st.session_state.messages.append({"role": "assistant", "content": m["content"]})
                    st.rerun()
        
        st.markdown("---")
        st.markdown("### ⚙️ Settings")
        st.button("User Preferences", use_container_width=True)
        st.button("Export Data", use_container_width=True)
        
        st.markdown("---")
        
        st.markdown("### System Status")
        st.success("✅ Multi-Agent Core: Online")
        st.success("✅ Vector DB (Qdrant): Online")
        
        st.markdown("---")
        st.markdown(
            "<div style='text-align: center; color: #9CA3AF; font-size: 0.8em;'>"
            "LegalGuide AI v1.0.0<br>Powered by LangGraph & Qdrant</div>", 
            unsafe_allow_html=True
        )
