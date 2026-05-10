from datetime import datetime, UTC
import os
from pathlib import Path
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from flask import Flask, abort, flash, redirect, render_template, request, url_for
import psycopg
import requests
import validators

from page_analyzer.urls_repository import (
    create_url,
    create_url_check,
    get_url_by_id,
    get_url_by_name,
    get_url_checks,
    get_urls,
)

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "secret-key")


def normalize_url(raw_url):
    parsed_url = urlparse(raw_url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}"


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
    title = normalize_text(title_tag.get_text(strip=True)) if title_tag else None
    description = (
        normalize_text(description_tag.get("content"))
        if description_tag is not None
        else None
    )

    return h1, title, description


def is_invalid_url(raw_url):
    return len(raw_url) > 255 or validators.url(raw_url) is not True


@app.get("/")
def index():
    return render_template("index.html", url="", error=None)


@app.post("/urls")
def create_url_route():
    raw_url = request.form.get("url", "").strip()

    if is_invalid_url(raw_url):
        error = "Некорректный URL"
        flash(error, "danger")
        return render_template("index.html", url=raw_url, error=error), 422

    normalized_url = normalize_url(raw_url)
    existing_url = get_url_by_name(normalized_url)
    if existing_url is not None:
        flash("Страница уже существует", "info")
        return redirect(url_for("show_url", id=existing_url["id"]))

    url_id = create_url(
        normalized_url,
        datetime.now(UTC).date(),
    )
    flash("Страница успешно добавлена", "success")
    return redirect(url_for("show_url", id=url_id))


@app.get("/urls")
def urls_index():
    urls = get_urls()
    return render_template("urls.html", urls=urls)


@app.get("/urls/<int:id>")
def show_url(id):
    url_item = get_url_by_id(id)
    if url_item is None:
        abort(404)
    checks = get_url_checks(id)
    return render_template("url.html", url_item=url_item, checks=checks)


@app.post("/urls/<int:id>/checks")
def create_check(id):
    url_item = get_url_by_id(id)
    if url_item is None:
        abort(404)

    try:
        response = requests.get(url_item["name"], timeout=10)
        response.raise_for_status()
        h1, title, description = extract_seo_data(response.text)

        create_url_check(
            url_id=id,
            status_code=response.status_code,
            h1=h1,
            title=title,
            description=description,
            created_at=datetime.now(UTC).date(),
        )
        flash("Страница успешно проверена", "success")
    except (requests.RequestException, psycopg.Error):
        flash("Произошла ошибка при проверке", "danger")

    return redirect(url_for("show_url", id=id))
