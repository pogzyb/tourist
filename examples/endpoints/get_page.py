from tourist.client import TouristScraper


tourist_scraper = TouristScraper(
    func_urls="https://gefg357mnsxojgcngmdxtcbzsi0feinb.lambda-url.us-east-1.on.aws/",
    x_api_key="secret-api-key",
)


if __name__ == "__main__":
    page = tourist_scraper.get_page("https://en.wikipedia.org/wiki/Dinosaur")
    print(page)
