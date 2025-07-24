from datetime import datetime

from services.search.qdrant_search_service import QdrantSearchService


class ImmigrationWebScrapeCronJob:

    def __init__(self):
        self.qdrant_search_service = QdrantSearchService()

    def scrape_immigration_info_weekly(self):
        pass

