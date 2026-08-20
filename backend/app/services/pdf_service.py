from pathlib import Path
from pypdf import PdfReader


def extract_text_from_pdf(file_path: Path):
    reader = PdfReader(file_path)

    pages = []
    total_text = ""

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        text = text.strip()

        pages.append({
            "page_number": page_number,
            "text": text
        })

        total_text += text

    return {
        "total_pages": len(pages),
        "pages": pages,
        "has_extractable_text": bool(total_text.strip())
    }