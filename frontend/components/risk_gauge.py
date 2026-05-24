import streamlit as st

def render_risk_gauge(risk: dict):
    """
    Renders a styled risk alert badge based on severity.
    """
    category = risk.get("risk_category", "Unknown Risk")
    description = risk.get("description", "No description provided.")
    severity = risk.get("severity", "Low").lower()
    
    # Define colors based on severity
    if severity == "high":
        border_color = "#EF4444"
        bg_color = "rgba(239, 68, 68, 0.1)"
        icon = "🚨"
    elif severity == "medium":
        border_color = "#F59E0B"
        bg_color = "rgba(245, 158, 11, 0.1)"
        icon = "⚠️"
    else:
        border_color = "#10B981"
        bg_color = "rgba(16, 185, 129, 0.1)"
        icon = "✅"
        
    html = f"""
    <div style="
        background: {bg_color};
        border: 1px solid {border_color};
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
    ">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <h4 style="margin: 0; color: #E5E7EB;">{icon} {category}</h4>
            <span style="
                background: {border_color}; 
                color: #ffffff; 
                padding: 2px 8px; 
                border-radius: 12px; 
                font-size: 0.8em; 
                font-weight: bold;
                text-transform: uppercase;
            ">
                {severity}
            </span>
        </div>
        <p style="color: #D1D5DB; font-size: 0.95em; margin-bottom: 0;">{description}</p>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
