from bs4 import BeautifulSoup


def normalize_text(value):
    if value is None:
        return None
    stripped_value = value.strip()
    return stripped_value or None


def extract_seo_data(html):
    soup = BeautifulSoup(html, "html.parser")

    h1_tag = soup.find("h1")
    title_tag = soup.find("title")
    description_tag = soup.find(
        "meta",
        attrs={
            "name": lambda tag_value: isinstance(tag_value, str)
            and tag_value.lower() == "description"
        },
    )

    h1 = normalize_text(h1_tag.get_text(strip=True)) if h1_tag else None
    title = (
        normalize_text(title_tag.get_text(strip=True))
        if title_tag
        else None
    )
    description = (
        normalize_text(description_tag.get("content"))
        if description_tag is not None
        else None
    )

    return h1, title, description
