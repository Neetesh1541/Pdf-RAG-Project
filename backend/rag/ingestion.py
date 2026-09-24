import re
from io import BytesIO
from pathlib import Path

import fitz
from PIL import Image
import pytesseract

OCR_MIN_CHARACTERS = 40


def clean_text(text: str) -> str:
    text = text.replace('\x00', ' ')
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def page_needs_ocr(text: str) -> bool:
    alpha_chars = sum(ch.isalpha() for ch in text)
    return len(text.strip()) < OCR_MIN_CHARACTERS or alpha_chars < 20


def ocr_pdf_page(page: fitz.Page) -> str:
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
    image = Image.open(BytesIO(pix.tobytes('png')))
    return pytesseract.image_to_string(image)


def process_document_file(file_path: str):
    pdf_path = Path(file_path)
    if not pdf_path.exists():
        raise FileNotFoundError('Uploaded PDF could not be located on disk.')

    try:
        doc = fitz.open(pdf_path)
    except Exception as exc:
        raise ValueError('Invalid or corrupted PDF file.') from exc

    if doc.page_count == 0:
        raise ValueError('The uploaded PDF is empty.')

    pages = []
    for page_index in range(doc.page_count):
        page = doc.load_page(page_index)
        text = page.get_text('text') or ''
        if page_needs_ocr(text):
            try:
                text = ocr_pdf_page(page)
            except Exception as exc:
                raise RuntimeError(f'OCR failed on page {page_index + 1}.') from exc
        pages.append({
            'page_number': page_index + 1,
            'text': clean_text(text),
        })

    doc.close()
    return pages
