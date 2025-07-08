import os
import fitz  # PyMuPDF
from pdf_to_chunk import extract_text_with_pymupdf, split_into_chunks

def extract_title_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    first_page = doc[0]
    blocks = first_page.get_text("dict")["blocks"]

    spans = []
    for block in blocks:
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                text = span["text"].strip()
                if not text:
                    continue
                spans.append({
                    "text": text,
                    "size": span["size"],
                    "font": span["font"],
                    "line": line,
                    "y": span["bbox"][1]
                })

    if not spans:
        return ""

    spans.sort(key=lambda x: x["size"], reverse=True)
    top_size = spans[0]["size"]
    top_spans = [s for s in spans if s["size"] >= top_size - 0.5]

    top_spans.sort(key=lambda x: x["y"])
    title_lines = [s["text"] for s in top_spans if not s["text"].lower().startswith(("review", "abstract", "doi"))]

    title = " ".join(title_lines).strip()
    if len(title) < 10:
        return ""
    return title

def process_pdf_dir(directory_path):
    all_chunks = []

    for filename in os.listdir(directory_path):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(directory_path, filename)
            text = extract_text_with_pymupdf(pdf_path)
            pdf_title = extract_title_from_pdf(pdf_path)
            chunks = split_into_chunks(text)
            for idx, chunk in enumerate(chunks):
                all_chunks.append({
                    "filename": filename,
                    "pdf_title": pdf_title,
                    "chunk_id": idx,
                    "text": chunk
                })

    return all_chunks

if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) != 2:
        print("사용법: python pdf_dir_to_chunks.py [PDF 디렉토리 경로]")
        sys.exit(1)

    dir_path = sys.argv[1]
    result = process_pdf_dir(dir_path)
    
    with open("chunks.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"{len(result)}개의 청크를 추출했습니다.")