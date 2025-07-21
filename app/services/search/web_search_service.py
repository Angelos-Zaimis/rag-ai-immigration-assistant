from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import Tool


class WebSearchService:


    @staticmethod
    def scrape_web_for_official_info(topic: str):
        search = DuckDuckGoSearchRun()
        return Tool(
            name="search_swiss_official_docs",
            description=f"Search official Swiss information about: {topic}",
            func=search.run
        )


