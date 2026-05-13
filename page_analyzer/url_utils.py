from urllib.parse import urlparse

import validators

MAX_URL_LENGTH = 255


def normalize_url(raw_url):
    parsed_url = urlparse(raw_url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}"


def is_invalid_url(raw_url):
    return len(raw_url) > MAX_URL_LENGTH or validators.url(raw_url) is not True
