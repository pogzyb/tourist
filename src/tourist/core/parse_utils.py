from urllib.parse import urlparse
from bs4 import BeautifulSoup as bs


def get_text(source_html: str) -> str:
    soup = bs(source_html, "html.parser")
    text = soup.get_text().replace("\n", " ")
    clean = " ".join(text.split())
    return clean


# TODO/Contribution: this function could be optimized in a few ways.
# Additional arguments could be added to "pick the best" links or exclude certain results.
def get_links_from_serp(source_html: str, engine: str) -> list[str]:
    # find all <a> tags and extract the "href"
    soup = bs(source_html, "html.parser")
    all_links = [ln.get("href") for ln in soup.find_all("a")]
    # external links only
    ext_links = [
        ln
        for ln in all_links
        if ln is not None and ln.startswith("http") and f"{engine}.com" not in ln
    ]
    # hostnames
    links = list(
        zip(
            map(
                lambda x: urlparse(x).hostname,
                ext_links,
            ),
            ext_links,
        )
    )
    # first link from every hostname? good enough.
    unique_links = []
    last_host = None
    for host, link in links:
        if host == last_host:
            continue
        unique_links.append(link)
        last_host = host

    return unique_links
