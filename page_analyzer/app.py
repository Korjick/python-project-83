from datetime import datetime, UTC
import os
from pathlib import Path

from dotenv import load_dotenv
from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
import psycopg
import requests

from page_analyzer.parser import extract_seo_data
from page_analyzer.url_utils import is_invalid_url, normalize_url
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
