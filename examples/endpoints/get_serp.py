from tourist.client import TouristScraper


tourist_scraper = TouristScraper(
    func_urls=["https://xxxxxxx.lambda-url.us-east-1.on.aws/"],
    x_api_key="secret-api-key",
)


if __name__ == "__main__":
    pages = tourist_scraper.get_serp("Winter olympics medal count 2026", "brave", timeout=300)
    print(pages)
