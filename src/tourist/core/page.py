import os
import shutil
from tempfile import mkdtemp
from contextlib import contextmanager

from pydantic import BaseModel
from selenium import webdriver
from selenium.common.exceptions import WebDriverException


CHROME_BIN = os.getenv("TOURIST__CHROME_BIN", "/tourist/browser/chrome")
CHROME_DRIVER = os.getenv("TOURIST__CHROME_DRIVER", "/tourist/browser/chromedriver")

DEFAULT_USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
DEFAULT_TIMEOUT = 28.0
DEFAULT_WINDOW_SIZE = (1920, 1080)


class Page(BaseModel):
    current_url: str
    source_html: str
    cookies: list
    b64_png: str | None = None


class PageActions(dict): ...


@contextmanager
def _chrome(
    user_agent: str,
    window_size: tuple[int, int] = DEFAULT_WINDOW_SIZE,
):
    window_width, window_height = window_size

    user_data_dir = mkdtemp(prefix="chrome-")
    data_path = mkdtemp(prefix="chrome-")
    disk_cache_dir = mkdtemp(prefix="chrome-")

    options = webdriver.ChromeOptions()
    options.binary_location = CHROME_BIN
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument(f"--window-size={window_width}x{window_height}")
    options.add_argument("--single-process")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-dev-tools")
    options.add_argument("--no-zygote")
    options.add_argument(f"--user-data-dir={user_data_dir}")
    options.add_argument(f"--data-path={data_path}")
    options.add_argument(f"--disk-cache-dir={disk_cache_dir}")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument(f"--user-agent={user_agent}")

    service = webdriver.ChromeService(CHROME_DRIVER)
    chrome = webdriver.Chrome(options=options, service=service)

    yield chrome
    chrome.quit()

    shutil.rmtree(user_data_dir)
    shutil.rmtree(data_path)
    shutil.rmtree(disk_cache_dir)


def get_page_with_actions(
    actions: str,
    user_agent: str = DEFAULT_USER_AGENT,
    timeout: float = DEFAULT_TIMEOUT,
    window_size: tuple[int, int] = DEFAULT_WINDOW_SIZE,
) -> PageActions | None:
    try:
        with _chrome(user_agent, window_size) as driver:
            # the actions script should use `actions_output` to store return values
            actions_output = {}
            driver.set_page_load_timeout(timeout)
            exec(actions)
            return PageActions(actions_output)
    except WebDriverException:
        return None


def get_page(
    target_url: str,
    warmup_url: str = None,
    cookies: list[dict[str, str]] = [],
    include_b64_png: bool = False,
    timeout: float = DEFAULT_TIMEOUT,
    user_agent: str = DEFAULT_USER_AGENT,
    window_size: tuple[int, int] = DEFAULT_WINDOW_SIZE,
) -> Page | None:
    try:
        with _chrome(user_agent, window_size) as driver:
            driver.set_page_load_timeout(timeout)

            if warmup_url is not None:
                driver.get(warmup_url)
                for cookie in cookies:
                    driver.add_cookie(cookie)

            driver.get(target_url)
            driver.implicitly_wait(1.0)

            data = {
                "source_html": driver.page_source,
                "cookies": driver.get_cookies(),
                "current_url": driver.current_url,
            }

            if include_b64_png:
                data["b64_png"] = driver.get_screenshot_as_base64()

            return Page(**data)
    except WebDriverException:
        return None
