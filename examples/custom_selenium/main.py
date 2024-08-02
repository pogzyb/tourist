from textwrap import dedent
from pprint import pprint

from tourist.core import TouristScraper

TOURIST_BASE = "http://localhost:8000"
TOURIST_X_SECRET = "doesntmatterlocally"

tourist_scraper = TouristScraper(
    base_url=TOURIST_BASE,
    secret=TOURIST_X_SECRET,
)


if __name__ == "__main__":

    # define your own function
    custom_func = dedent(
        """
def my_selenium_function(driver, actions_output):
    driver.get("https://www.example.com")
    driver.implicitly_wait(2)
    actions_output["current_url"] = driver.current_url

my_selenium_function(driver, actions_output)
"""
    )
    data = tourist_scraper.do_actions(custom_func)
    pprint(data)

    # pass a script
    line_by_line = dedent(
        """from selenium.webdriver.common.by import By

driver.get("https://www.example.com")
links = driver.find_elements(By.TAG_NAME, "a")
links[0].click()
driver.implicitly_wait(2)
actions_output["current_url"] = driver.current_url"""
    )

    data = tourist_scraper.do_actions(custom_func)
    pprint(data)
