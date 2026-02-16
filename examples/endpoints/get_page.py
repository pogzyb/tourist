from tourist.client import TouristScraper


tourist_scraper = TouristScraper(
    base_url="https://xxxxxxxxx.lambda-url.us-east-1.on.aws",
    x_api_key="SEECRETTTKEYYY",
)


if __name__ == "__main__":
    page = tourist_scraper.get_page(
        "https://en.wikipedia.org/wiki/Dinosaur", timeout=300
    )
    print(page)
