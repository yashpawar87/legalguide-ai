import fitz
import pytesseract
from PIL import Image
import io
import re
import unicodedata

def clean_text(text: str) -> str:
    # 1. Fix Unicode artifacts (e.g., smart quotes, weird spacing from PDFs)
    # NFKD normalizes characters to their standard equivalents
    text = unicodedata.normalize('NFKD', text)
    
    # 2. Handle horizontal whitespace ONLY (spaces and tabs)
    # This prevents us from accidentally deleting newlines
    text = re.sub(r'[ \t]+', ' ', text)
    
    # 3. Fix mid-sentence line breaks (Common in Indian Court PDFs)
    # If a newline is followed by a lowercase letter, it's likely a broken sentence.
    # e.g., "in \n Writ Petition" -> "in Writ Petition"
    text = re.sub(r'(?<=[a-z])\n(?=[a-z])', ' ', text)
    
    # 4. Normalize multiple newlines into a single standard newline
    text = re.sub(r'\n+', '\n', text)
    
    # 5. Remove leading/trailing whitespace from the entire string
    text = text.strip()
    
    return text


def extract_text_from_pdf(file_path: str) -> list[dict]:

    doc = fitz.open(file_path)

    pages = []

    for page_num, page in enumerate(doc):

        raw_text = page.get_text('text')
        text = clean_text(raw_text)

        if len(text) > 50:

            pages.append({
                'page_num': page_num + 1,
                'text': text,
                'extraction_method': 'pymupdf'
            })

        else:

            pix = page.get_pixmap(dpi=300)

            img = Image.open(
                io.BytesIO(
                    pix.tobytes('png')
                )
            )

            ocr_text = pytesseract.image_to_string(
                img,
                lang='eng'
            )
            
            ocr_text = clean_text(ocr_text)

            pages.append({
                'page_num': page_num + 1,
                'text': ocr_text,
                'extraction_method': 'ocr'
            })

    return pages 