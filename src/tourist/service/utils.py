from urllib.parse import urlparse

from bs4 import BeautifulSoup as bs


# TODO/Contribution: this function could be optimized in a few ways.
# Additional arguments could be added to "pick the best" links or exclude certain results.
def get_links_from_serp(
    source_html: str,
    engine: str,
    exclude_hosts: list[str] = [],
) -> list[str]:
    soup = bs(source_html, "html.parser")
    all_links = [ln.get("href") for ln in soup.find_all("a")]
    ext_links = [
        ln
        for ln in all_links
        if ln is not None
        and ln.startswith("http")
        and f".{engine}.com" not in ln
        and not any([h in ln for h in exclude_hosts])
    ]
    links = list(
        zip(
            map(
                lambda x: urlparse(x).hostname,
                ext_links,
            ),
            ext_links,
        )
    )
    unique_links = []
    last_host = None
    for host, link in links:
        if host == last_host:
            continue
        unique_links.append(link)
        last_host = host
    return unique_links
