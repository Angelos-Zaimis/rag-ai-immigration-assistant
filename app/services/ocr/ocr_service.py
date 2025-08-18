from pytesseract import pytesseract
import time
from utils.utils import create_temp_file, clean_ocr_text, logger, cleanup_temp_file, get_tesseract_language_code
from pdf2image import convert_from_path
from PIL import Image

class OCRService:
    """Service for OCR text extraction from images and PDFs"""

    def __init__(self):
        self.max_retries = 3
        self.retry_delay = 1  # seconds

    def extract_text_from_file(self, uploaded_file, language: str = 'en') -> str:
        file_name = uploaded_file.name.lower()

        if file_name.endswith('.pdf'):
            return self._extract_text_from_pdf(uploaded_file, language)
        else:
            return self._extract_text_from_image(uploaded_file, language)

    def _extract_text_from_pdf(self, uploaded_file, language: str) -> str:
        """Convert PDF to image and extract text"""
        temp_pdf_path = None

        try:
            # Create temporary PDF file
            temp_pdf_path = create_temp_file(uploaded_file, '.pdf')

            # Convert PDF to images
            images = convert_from_path(temp_pdf_path)

            # Extract text from all pages
            all_text = []
            for i, image in enumerate(images):
                text = self._extract_text_from_image_object(image, language)
                if text.strip():
                    all_text.append(f"Page {i + 1}:\n{text}")

            # Clean and join text
            combined_text = '\n\n'.join(all_text)
            return clean_ocr_text(combined_text)

        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise Exception(f"PDF processing failed: {str(e)}")
        finally:
            # Clean up temporary file
            if temp_pdf_path:
                cleanup_temp_file(temp_pdf_path)

    def _extract_text_from_image(self, uploaded_file, language: str) -> str:
        """Extract text from image file"""
        try:
            # Open image using PIL
            image = Image.open(uploaded_file)
            return self._extract_text_from_image_object(image, language)
        except Exception as e:
            logger.error(f"Error extracting text from image: {e}")
            raise Exception(f"Image processing failed: {str(e)}")

    def _extract_text_from_image_object(self, image: Image.Image, language: str) -> str:
        """Extract text from PIL Image object with retry logic"""

        for attempt in range(self.max_retries):
            try:
                # Configure tesseract for the specified language
                tesseract_lang = get_tesseract_language_code(language)
                custom_config = f'--oem 3 --psm 6 -l {tesseract_lang}'

                # Extract text
                text = pytesseract.image_to_string(image, config=custom_config)

                # Clean the extracted text
                cleaned_text = clean_ocr_text(text)

                if cleaned_text.strip():
                    return cleaned_text
                else:
                    logger.warning(f"No text extracted on attempt {attempt + 1}")

            except Exception as e:
                logger.error(f"OCR attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    raise Exception(f"OCR failed after {self.max_retries} attempts: {str(e)}")

        return ""