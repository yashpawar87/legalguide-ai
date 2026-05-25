import io
import re
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.colors import HexColor

def clean_markdown(text: str) -> str:
    """
    Converts basic markdown into ReportLab compatible HTML/XML tags.
    """
    if not text:
        return ""
    # Convert **bold** to <b>bold</b>
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    # Remove # headers
    text = re.sub(r'#+\s*(.*)', r'<b>\1</b>', text)
    # Convert newlines to breaks
    text = text.replace('\n', '<br/>')
    return text

def generate_legal_report(message: dict) -> bytes:
    """
    Generates a formatted PDF report from the AI's response dictionary or string.
    Returns the PDF as an in-memory byte stream.
    """
    buffer = io.BytesIO()
    
    # Configure document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Styles
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=HexColor('#4F46E5'),
        spaceAfter=30
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=HexColor('#111827'),
        spaceBefore=20,
        spaceAfter=10
    )
    
    normal_style = styles['Normal']
    normal_style.fontSize = 11
    normal_style.leading = 14
    
    risk_high_style = ParagraphStyle(
        'RiskHigh',
        parent=normal_style,
        textColor=HexColor('#DC2626')
    )
    
    risk_med_style = ParagraphStyle(
        'RiskMed',
        parent=normal_style,
        textColor=HexColor('#D97706')
    )
    
    story = []
    
    # Header
    story.append(Paragraph("LegalGuide AI - Automated Analysis", title_style))
    
    # Handle plain text fallback (from DB)
    if "result" not in message:
        content = message.get("content", "")
        story.append(Paragraph(clean_markdown(content), normal_style))
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
        
    result = message["result"]
    
    # 1. Main Report
    story.append(Paragraph("Legal Analysis Report", heading_style))
    report_text = result.get("final_report", "")
    story.append(Paragraph(clean_markdown(report_text), normal_style))
    story.append(Spacer(1, 20))
    
    # 2. Risks
    risks = result.get("risks", [])
    if risks:
        story.append(Paragraph("Risk Assessment", heading_style))
        for risk in risks:
            severity = risk.get("severity", "low").lower()
            style = risk_high_style if severity == "high" else (risk_med_style if severity == "medium" else normal_style)
            
            risk_text = f"<b>[{severity.upper()}] {risk.get('risk_category', 'Risk')}:</b> {risk.get('description', '')}"
            story.append(Paragraph(clean_markdown(risk_text), style))
            story.append(Spacer(1, 5))
            
    # 3. Statutes
    statutes = result.get("statutes", [])
    if statutes:
        story.append(Paragraph("Relevant Laws & Sections", heading_style))
        for s in statutes:
            stat_text = f"<b>{s.get('act_name', '')} - Sec {s.get('section_number', '')}</b>: {s.get('section_title', '')}<br/><i>Relevance:</i> {s.get('relevance_explanation', '')}"
            story.append(Paragraph(clean_markdown(stat_text), normal_style))
            story.append(Spacer(1, 10))
            
    # 4. Precedents
    precedents = result.get("precedents", [])
    if precedents:
        story.append(Paragraph("Precedent Cases", heading_style))
        for p in precedents:
            prec_text = f"<b>{p.get('case_name', '')}</b> ({p.get('year', '')}) - {p.get('court', '')}<br/><i>Citation:</i> {p.get('citation', '')}<br/><i>Holding:</i> {p.get('holding', '')}<br/><i>Relevance:</i> {p.get('relevance', '')}"
            story.append(Paragraph(clean_markdown(prec_text), normal_style))
            story.append(Spacer(1, 10))
            
    # Build Document
    doc.build(story)
    
    buffer.seek(0)
    return buffer.getvalue()
