import re
import os
import tempfile
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


def get_tesseract_language_code(language: str) -> str:
    """Convert common language codes to Tesseract language codes"""
    language_mapping = {
        'en': 'eng',  # English
        'de': 'deu',  # German
        'fr': 'fra',  # French
        'es': 'spa',  # Spanish
        'it': 'ita',  # Italian
        'pt': 'por',  # Portuguese
        'ru': 'rus',  # Russian
        'ar': 'ara',  # Arabic
        'zh': 'chi_sim',  # Chinese Simplified
        'ja': 'jpn',  # Japanese
        'ko': 'kor',  # Korean
        'gr': 'ell',  # Greek
        'nl': 'nld',  # Dutch
        'pl': 'pol',  # Polish
        'tr': 'tur',  # Turkish
        'sv': 'swe',  # Swedish
        'da': 'dan',  # Danish
        'no': 'nor',  # Norwegian
        'fi': 'fin',  # Finnish
        'cs': 'ces',  # Czech
        'sk': 'slk',  # Slovak
        'hu': 'hun',  # Hungarian
        'ro': 'ron',  # Romanian
        'bg': 'bul',  # Bulgarian
        'hr': 'hrv',  # Croatian
        'sr': 'srp',  # Serbian
        'sl': 'slv',  # Slovenian
        'et': 'est',  # Estonian
        'lv': 'lav',  # Latvian
        'lt': 'lit',  # Lithuanian
    }

    # Return mapped code or original if not found
    return language_mapping.get(language.lower(), language.lower())


def clean_ocr_text(text: str) -> str:
    """
    Clean OCR extracted text by removing noise, artifacts, and normalizing formatting
    Args:
        text: Raw OCR text
    Returns:
        Cleaned text
    """
    if not text:
        return ""

    # Remove excessive whitespace and normalize line breaks
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)  # Multiple line breaks to double
    text = re.sub(r' +', ' ', text)  # Multiple spaces to single
    text = re.sub(r'\t+', ' ', text)  # Tabs to spaces

    # Remove common OCR artifacts
    text = re.sub(r'[^\w\s\.,!?;:()\[\]{}"\'-]', '', text)  # Remove special chars except common punctuation

    # Fix common OCR mistakes
    text = re.sub(r'(\d+)\s*\.\s*(\d+)', r'\1.\2', text)  # Fix decimal numbers
    text = re.sub(r'(\w+)\s*-\s*(\w+)', r'\1-\2', text)  # Fix hyphenated words

    # Remove isolated characters (likely OCR noise)
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        if len(line) > 1 or line.isdigit():  # Keep lines with more than 1 char or digits
            cleaned_lines.append(line)

    # Join lines and final cleanup
    text = '\n'.join(cleaned_lines)
    text = text.strip()

    return text


def create_temp_file(uploaded_file, suffix: str = '') -> str:
    """
    Create a temporary file from uploaded file
    Args:
        uploaded_file: Django uploaded file
        suffix: File suffix (e.g., '.pdf')
    Returns:
        Path to temporary file
    """
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)

    try:
        for chunk in uploaded_file.chunks():
            temp_file.write(chunk)
        temp_file.close()
        return temp_file.name
    except Exception as e:
        # Clean up on error
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
        raise e


def cleanup_temp_file(file_path: str) -> None:
    """
    Safely remove temporary file
    Args:
        file_path: Path to temporary file
    """
    try:
        if file_path and os.path.exists(file_path):
            os.unlink(file_path)
    except Exception as e:
        logger.warning(f"Failed to cleanup temp file {file_path}: {e}")


def validate_file_size(file_size: int, max_size_mb: int = 10) -> bool:
    """
    Validate file size
    Args:
        file_size: File size in bytes
        max_size_mb: Maximum size in MB
    Returns:
        True if file size is valid
    """
    max_size_bytes = max_size_mb * 1024 * 1024
    return file_size <= max_size_bytes


def get_file_extension(filename: str) -> str:
    """
    Get file extension from filename
    Args:
        filename: Name of the file
    Returns:
        File extension (lowercase, without dot)
    """
    return os.path.splitext(filename)[1].lower().lstrip('.')


def is_supported_file_type(filename: str) -> bool:
    """
    Check if file type is supported
    Args:
        filename: Name of the file
    Returns:
        True if file type is supported
    """
    supported_extensions = {'jpg', 'jpeg', 'png', 'gif', 'pdf'}
    extension = get_file_extension(filename)
    return extension in supported_extensions