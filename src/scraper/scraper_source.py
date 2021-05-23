from bs4 import BeautifulSoup

from .scrape_container import ScrapeContainer

class ScraperParser:
    name: str

    def isSupported(self, link) -> str: # If supported a id is returned
        return None

    def parse(self, container: ScrapeContainer, link: str, priority: int, id: str, soup: BeautifulSoup):
        pass