import streamlit as st
import time
from components.sidebar import render_sidebar
from components.citation_card import render_statute, render_precedent
from components.risk_gauge import render_risk_gauge
from components.risk_gauge import render_risk_gauge
from utils.auth import sign_in_with_email_and_password
from utils.api_client import analyze_query, upload_document, create_chat_session
from utils.pdf_generator import generate_legal_report

st.set_page_config(
    page_title="LegalGuide AI | Chat",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium Global CSS
st.markdown("""
<style>
    /* Global background */
    .stApp {
        background-color: #0F172A;
        color: #F3F4F6;
    }
    
    /* Typography */
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
    }
    
    .gradient-text {
        background: linear-gradient(90deg, #4F46E5, #10B981);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Input styling */
    .stTextInput>div>div>input {
        background-color: rgba(255,255,255,0.05);
        color: white;
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 8px;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #4F46E5, #3B82F6);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.4);
    }
    
    /* Hide Streamlit default UI elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ----------------- AUTHENTICATION GATE -----------------
if "id_token" not in st.session_state:
    st.session_state.id_token = None
    
if not st.session_state.id_token:
    st.markdown("<h1 class='gradient-text' style='text-align: center; font-size: 4rem; margin-top: 10vh;'>LegalGuide AI</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #9CA3AF; font-weight: 300;'>Secure Access Required</h3>", unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Secure Login")
            
            if submit:
                if not email or not password:
                    st.error("Please enter both email and password.")
                else:
                    with st.spinner("Authenticating..."):
                        result = sign_in_with_email_and_password(email, password)
                        if "error" in result:
                            st.error(result["error"])
                        else:
                            st.session_state.id_token = result["idToken"]
                            st.session_state.user_email = result["email"]
                            st.rerun()
    st.stop()


# ----------------- UNIFIED CHAT APP -----------------
render_sidebar()

@st.cache_data(show_spinner=False, max_entries=20)
def get_pdf_bytes(msg_str: str, _msg: dict) -> bytes:
    return generate_legal_report(_msg)

# Initialize Chat State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_document_id" not in st.session_state:
    st.session_state.current_document_id = None
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None

# Header & Info Box
st.markdown("<h1 class='gradient-text' style='text-align: center; font-size: 3rem;'>LegalGuide AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #9CA3AF;'>How can I assist with your legal research today?</p>", unsafe_allow_html=True)

with st.expander("📄 Upload Document Context (Optional)"):
    st.info("Upload a document (PDF, JPG, PNG) to give the AI specific context for your queries.")
    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "jpg", "jpeg", "png"])
    if uploaded_file and st.button("Upload & Process"):
        with st.spinner("Uploading..."):
            file_bytes = uploaded_file.getvalue()
            res = upload_document(file_bytes, uploaded_file.name)
            if "error" in res:
                st.error(res["error"])
            else:
                st.success(f"Processed: {uploaded_file.name}")
                st.session_state.current_document_id = str(res.get("id", ""))

st.markdown("---")

# Render Chat History
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(msg["content"])
    else:
        with st.chat_message("assistant"):
            if "result" in msg:
                result = msg["result"]
                
                # Action Toolbar
                col_d, col_s, col_sv, _ = st.columns([2,2,2,10])
                
                pdf_bytes = get_pdf_bytes(str(msg), msg)
                col_d.download_button(
                    label="⬇️ Download PDF",
                    data=pdf_bytes,
                    file_name=f"legal_report_{msg.get('id', int(time.time()))}.pdf",
                    mime="application/pdf",
                    key=f"d_{msg.get('id', 0)}"
                )
                
                col_s.button("🔗 Share", key=f"s_{msg.get('id', 0)}")
                col_sv.button("💾 Save", key=f"sv_{msg.get('id', 0)}")
                
                # Main Report
                st.markdown("### 📑 Legal Analysis Report")
                st.markdown(f"""
                <div style="background: rgba(255, 255, 255, 0.05); padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                    {result.get('final_report', '')}
                </div>
                """, unsafe_allow_html=True)
                
                # Risk Assessment Native Alerts
                st.markdown("### 🚨 Risk Assessment")
                risks = result.get("risks", [])
                if not risks:
                    st.success("No major legal risks identified.")
                for risk in risks:
                    severity = risk.get("severity", "Low").lower()
                    msg_text = f"**{risk.get('risk_category', 'Risk')}**: {risk.get('description', '')}"
                    if severity == "high":
                        st.error(msg_text)
                    elif severity == "medium":
                        st.warning(msg_text)
                    else:
                        st.success(msg_text)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Expanders for Laws and Precedents
                col1, col2 = st.columns(2)
                with col1:
                    with st.expander("📜 Relevant Laws & Sections", expanded=True):
                        statutes = result.get("statutes", [])
                        if not statutes:
                            st.info("No applicable statutes extracted.")
                        for s in statutes:
                            render_statute(s)
                            
                with col2:
                    with st.expander("⚖️ Precedent Cases", expanded=True):
                        precedents = result.get("precedents", [])
                        if not precedents:
                            st.info("No relevant precedents found.")
                        for p in precedents:
                            render_precedent(p)
                            
                # Citations
                st.markdown("---")
                st.markdown("**Citations:**")
                citations = result.get('citations', [])
                if citations:
                    for c in citations:
                        st.caption(f"[{'Verified' if c.get('verified') else 'Unverified'}] {c.get('source_type')}: {c.get('reference')}")
                else:
                    st.caption("No explicit citations provided.")
            else:
                # Fallback for historical messages loaded from DB which only have 'content' string
                
                # Action Toolbar
                col_d, col_s, col_sv, _ = st.columns([2,2,2,10])
                pdf_bytes = get_pdf_bytes(str(msg), msg)
                col_d.download_button(
                    label="⬇️ Download PDF",
                    data=pdf_bytes,
                    file_name=f"legal_report_{msg.get('id', int(time.time()))}.pdf",
                    mime="application/pdf",
                    key=f"d_{msg.get('id', 0)}_hist"
                )
                col_s.button("🔗 Share", key=f"s_{msg.get('id', 0)}_hist")
                col_sv.button("💾 Save", key=f"sv_{msg.get('id', 0)}_hist")
                
                st.markdown("### 📑 Legal Analysis Report")
                st.markdown(f"""
                <div style="background: rgba(255, 255, 255, 0.05); padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                    {msg.get('content', '')}
                </div>
                """, unsafe_allow_html=True)

# Input Field
query = st.chat_input("Enter your legal query or ask a follow-up question...")

if query:
    # 1. Display user query
    with st.chat_message("user"):
        st.markdown(query)
    
    # 2. Add to history
    st.session_state.messages.append({"role": "user", "content": query})
    
    # Process with AI
    with st.chat_message("assistant"):
        # Loading State sequence
        with st.status("Analyzing your legal query...", expanded=True) as status:
            # 2.5 Ensure session exists
            if not st.session_state.current_session_id:
                st.write("Initializing new secure chat session...")
                title = query[:50] + "..." if len(query) > 50 else query
                sess = create_chat_session(title)
                if "id" in sess:
                    st.session_state.current_session_id = sess["id"]

            st.write("Extracting text (OCR)...")
            time.sleep(0.5)
            st.write("Retrieving legal corpus (BNSS, IPC, Precedents)...")
            time.sleep(0.5)
            st.write("Running multi-agent analysis...")
            
            # Actual API Call
            result = analyze_query(query, st.session_state.current_document_id, st.session_state.current_session_id)
            
            st.write("Synthesizing insights...")
            time.sleep(0.5)
            status.update(label="Analysis Complete!", state="complete", expanded=False)
        
        if "error" in result:
            st.error(result["error"])
        else:
            # Store in history and rerun to render properly via the loop above
            st.session_state.messages.append({
                "role": "assistant", 
                "result": result,
                "id": len(st.session_state.messages)
            })
            st.rerun()
