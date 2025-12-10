from tourist.client import TouristScraper


tourist_scraper = TouristScraper(
    base_url="https://tbbsgfsuvid4n5xnd6yiwrhyqe0hwufe.lambda-url.us-east-1.on.aws",
    x_api_key="SEECRETTTKEYYY",
)


if __name__ == "__main__":
    pages = tourist_scraper.get_serp("College Football Playoffs", "google")
    print(pages)
