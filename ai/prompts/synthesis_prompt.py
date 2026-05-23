from langchain_core.prompts import PromptTemplate

SYNTHESIS_PROMPT = PromptTemplate(
    template="""
    You are the Lead Legal Counsel orchestrating a final report. Synthesize the findings from your 
    specialized legal agents into a highly professional, structured, and comprehensive final report 
    for the user.
    
    Original Query: {query}
    
    --- Agent Findings ---
    Analysis:
    {analysis}
    
    Applicable Statutes:
    {statutes_str}
    
    Precedents:
    {precedents_str}
    
    Identified Risks:
    {risks_str}
    
    Citations:
    {citations_str}
    
    Provide the final synthesized report:
    """,
    input_variables=["query", "analysis", "statutes_str", "precedents_str", "risks_str", "citations_str"]
)
