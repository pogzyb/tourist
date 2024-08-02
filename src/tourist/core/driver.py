import os
import shutil
import logging
from pathlib import Path
from tempfile import mkdtemp
from contextlib import contextmanager

from pydantic import BaseModel
from selenium import webdriver
from selenium.common.exceptions import WebDriverException

from tourist.core.utils import retry

CHROME_BIN = os.getenv("TOURIST__CHROME_BIN", "/tourist/browser/chrome")
CHROME_DRIVER = os.getenv("TOURIST__CHROME_DRIVER", "/tourist/browser/chromedriver")

DEFAULT_USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
DEFAULT_TIMEOUT = 15.0
DEFAULT_WINDOW_SIZE = (1920, 1080)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class Page(BaseModel):
    current_url: str
    source_html: str
    cookies: list
    b64_screenshot: str | None = None


class PageActions(dict): ...


@contextmanager
def _chrome(
    user_agent: str,
    window_size: tuple[int, int] = DEFAULT_WINDOW_SIZE,
):
    chrome = None
    try:
        window_width, window_height = window_size

        user_data_dir = mkdtemp(prefix="chrome-")
        data_path = mkdtemp(prefix="chrome-")
        disk_cache_dir = mkdtemp(prefix="chrome-")

        # TODO/Contribution: Add support for proxy
        options = webdriver.ChromeOptions()
        options.binary_location = CHROME_BIN
        options.add_argument("-headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument(f"--window-size={window_width}x{window_height}")
        options.add_argument("--single-process")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-dev-tools")
        options.add_argument("--deny-permission-prompts")
        options.add_argument("--no-zygote")
        options.add_argument(f"--user-data-dir={user_data_dir}")
        options.add_argument(f"--data-path={data_path}")
        options.add_argument(f"--disk-cache-dir={disk_cache_dir}")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--remote-debugging-port=9222")
        options.add_argument(f"--user-agent={user_agent}")
        # turn off geolocation
        prefs = {"profile.default_content_setting_values.geolocation": 2}
        options.add_experimental_option("prefs", prefs)

        service = webdriver.ChromeService(CHROME_DRIVER)
        chrome = webdriver.Chrome(options=options, service=service)

        logger.debug("Created chromedriver context.")
        yield chrome

    except WebDriverException:
        raise

    finally:
        if chrome is not None and hasattr(chrome, "quit"):
            logger.debug("Closing chromedriver.")
            chrome.quit()

        logger.debug("Deleting /tmp/chrome-* directories.")
        if Path(user_data_dir).is_dir():
            shutil.rmtree(user_data_dir)
        if Path(data_path).is_dir():
            shutil.rmtree(data_path)
        if Path(disk_cache_dir).is_dir():
            shutil.rmtree(disk_cache_dir)
        logger.debug("Returning from chrome contextmanager.")


@retry(n=1)
def get_page_with_actions(
    actions: str,
    user_agent: str = DEFAULT_USER_AGENT,
    timeout: float = DEFAULT_TIMEOUT,
    window_size: tuple[int, int] = DEFAULT_WINDOW_SIZE,
) -> PageActions | None:
    with _chrome(user_agent, window_size) as driver:
        driver.set_page_load_timeout(timeout)

        # `actions_output` can store results from the given script
        actions_output = {}

        exec(f"""{actions}""")

        return PageActions(actions_output)


@retry(n=1)
def get_page(
    target_url: str,
    warmup_url: str = None,
    cookies: list[dict[str, str]] = [],
    screenshot: bool = False,
    timeout: float = DEFAULT_TIMEOUT,
    user_agent: str = DEFAULT_USER_AGENT,
    window_size: tuple[int, int] = DEFAULT_WINDOW_SIZE,
) -> Page | None:
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

        if screenshot:
            data["b64_screenshot"] = driver.get_screenshot_as_base64()

        return Page(**data)
