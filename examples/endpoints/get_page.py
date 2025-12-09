from tourist.client import TouristScraper


tourist_scraper = TouristScraper(
    base_url="http://localhost:8000",
    x_api_key="supersecret",
)


if __name__ == "__main__":
    page = tourist_scraper.get_page("https://en.wikipedia.org/wiki/Dinosaur")
    print(page)
