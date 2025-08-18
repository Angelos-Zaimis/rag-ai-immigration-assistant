import os
from typing import Dict, Any, Optional

from google.cloud import translate_v2 as translate

from utils.utils import logger


class TranslationService:
    """Service for translating analysis results"""

    def __init__(self):
        self.api_key = os.environ.get('GOOGLE_TRANSLATE_API_KEY')

    def translate_text(self, text: str, user_language: str) -> dict | list | str:
        try:
            if self.api_key:
                return self._translate_with_google(text, user_language)
            else:
                logger.warning("No API key available for translation")
                return text
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return text

    def _translate_with_google(self, text: str, target_language: str) -> dict | list:
        try:
            client = translate.Client(api_key=self.api_key)
            translated_text = client.translate(text, target_language=target_language)

            return translated_text

        except Exception as e:
            logger.error(f"GPT translation failed: {e}")