import pdfplumber
import re

import fitz  # PyMuPDF

def extract_text_with_pymupdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

    
def split_into_chunks(text, max_chars=800):
    sentences = re.split(r'(?<=[.!?]) +', text)  # 문장 기준 분할
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) < max_chars:
            current_chunk += sentence + " "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("사용법: python pdf_to_chunk.py [PDF 파일 경로]")
        sys.exit(1)

    pdf_path = sys.argv[1]
    text = extract_text_with_pymupdf(pdf_path)
    chunks = split_into_chunks(text)

    for i, chunk in enumerate(chunks):
        print(f"\n--- 청크 {i+1} ---\n")
        print(chunk)