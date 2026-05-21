import spacy
import re
import subprocess
import sys

# Ensure the spacy model is downloaded
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading spaCy model 'en_core_web_sm'...")
    subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

def extract_entities(text: str) -> dict:
    doc = nlp(text)
    
    results = {
        "court_name": None,
        "judge_names": set(),
        "party_names": [],
        "dates": set(),
        "ipc_bns_sections": set()
    }
    
    # 1. Dates (Using spaCy NER)
    for ent in doc.ents:
        if ent.label_ == "DATE":
            cleaned_date = ent.text.strip().replace('\n', ' ')
            if len(cleaned_date) > 3: # Ignore very short artifacts
                results["dates"].add(cleaned_date)
                
    # 2. Court Name (Regex)
    # Matches common court headers, e.g., "IN THE HIGH COURT OF..." or "THE SUPREME COURT OF..."
    court_pattern = re.compile(r"(IN THE (?:HIGH COURT|SUPREME COURT)[\w\s,]+)", re.IGNORECASE)
    court_match = court_pattern.search(text)
    if court_match:
        # Stop at the first newline or extra spaces
        court_name = court_match.group(1).strip().replace('\n', ' ')
        court_name = re.sub(r'\s{2,}', ' ', court_name)
        results["court_name"] = court_name

    # 3. Judge Names (Regex + Context)
    judge_patterns = [
        r"HON['’]?BLE\s+(?:MR\.|MRS\.|MS\.)?\s*JUSTICE\s+([A-Z][A-Za-z\s\.]+)",
        r"CORAM\s*:\s*([A-Z][A-Za-z\s\.,]+)"
    ]
    for pattern in judge_patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            name = match.group(1).strip().replace('\n', ' ')
            # Stop at the first newline or double space or connective words
            name = re.split(r'  | AND | OR ', name)[0].strip()
            if len(name) > 3:
                results["judge_names"].add(name)

    # 4. Party Names (Regex for v. / vs. / versus)
    # Looking for lines containing 'vs', 'v.', or 'versus' as standalone words
    lines = text.split('\n')
    for i, line in enumerate(lines):
        if re.search(r'\b(?:vs\.?|v\.?|versus)\b', line, re.IGNORECASE):
            # Try to capture the block before and after
            petitioner_lines = [l.strip() for l in lines[max(0, i-4):i] if l.strip()]
            respondent_lines = [l.strip() for l in lines[i+1:min(len(lines), i+5)] if l.strip()]
            
            petitioner = petitioner_lines[-1] if petitioner_lines else ""
            respondent = respondent_lines[0] if respondent_lines else ""
            
            # Remove "..." or ". . ." commonly found in PDF party names
            petitioner = re.sub(r'^\.+|\.+$', '', petitioner).strip()
            respondent = re.sub(r'^\.+|\.+$', '', respondent).strip()
            
            if petitioner and respondent:
                results["party_names"].append(f"{petitioner} vs {respondent}")
            break # Just take the first match as it's usually the main case title

    # 5. Mentioned IPC/BNS/CrPC sections
    # Matches "Section 302 of IPC", "U/s 420 IPC", "Sections 120B/34 of the Indian Penal Code"
    section_pattern = re.compile(r"(?:Section|U/s|Sections)\s+([\d\w\s,/]+)\s+(?:of\s+)?(?:the\s+)?(IPC|Indian Penal Code|BNS|Bharatiya Nyaya Sanhita|CrPC|Code of Criminal Procedure)", re.IGNORECASE)
    for match in section_pattern.finditer(text):
        sec = match.group(1).strip()
        act = match.group(2).strip()
        # Normalizing spaces
        sec = re.sub(r'\s+', ' ', sec)
        act = re.sub(r'\s+', ' ', act)
        results["ipc_bns_sections"].add(f"Section {sec} of {act}")
        
    # Convert sets to lists for JSON serializability (and sort for consistency)
    results["judge_names"] = sorted(list(results["judge_names"]))
    results["dates"] = sorted(list(results["dates"]))
    results["ipc_bns_sections"] = sorted(list(results["ipc_bns_sections"]))
    
    return results
