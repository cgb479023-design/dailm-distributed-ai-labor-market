import os
import logging
from typing import List
try:
    from PIL import Image
    import pytesseract
    import fitz  # PyMuPDF
except ImportError:
    pass

logger = logging.getLogger("OCR_ENGINE")

class OCREngine:
    """
    High-precision OCR extraction for scanned bidding documents.
    Requires Tesseract-OCR installed on the system.
    """
    def __init__(self, tesseract_cmd: str = None):
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        
    def extract_from_pdf(self, pdf_path: str) -> str:
        """Converts PDF pages to images and runs OCR on each."""
        logger.info(f"[OCR]: Initializing deep scan for {pdf_path}")
        full_text = []
        
        try:
            doc = fitz.open(pdf_path)
            for i, page in enumerate(doc):
                logger.info(f"Processing page {i+1}/{len(doc)}...")
                pix = page.get_pixmap()
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                
                # Run OCR
                page_text = pytesseract.image_to_string(img, lang='chi_sim+eng')
                full_text.append(page_text)
            
            doc.close()
            return "\n".join(full_text)
        except Exception as e:
            logger.error(f"OCR Extraction failed: {e}")
            return f"ERROR: OCR failed for {pdf_path}"

    def is_scanned(self, pdf_path: str) -> bool:
        """Heuristic to detect if a PDF is likely a scanned image."""
        try:
            from pypdf import PdfReader
            reader = PdfReader(pdf_path)
            # If text density is very low across first 5 pages, it's scanned
            text_len = 0
            for i in range(min(5, len(reader.pages))):
                text_len += len(reader.pages[i].extract_text().strip())
            return text_len < 100
        except:
            return True

if __name__ == "__main__":
    # Test stub
    ocr = OCREngine()
    # print(ocr.extract_from_pdf("path_to_scanned.pdf"))
