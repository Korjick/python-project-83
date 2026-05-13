# Page Analyzer

[![Actions Status](https://github.com/Korjick/python-project-83/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/Korjick/python-project-83/actions)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=Korjick_python-project-83&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=Korjick_python-project-83)

Page Analyzer is a Flask web application for checking websites for basic SEO
metadata. It stores submitted URLs, runs page checks, and shows status codes,
titles, H1 headings, and meta descriptions.

## Demo

[Open deployed application on Render](https://page-analyzer-x9y8.onrender.com)

## Technologies

| Tool | Purpose |
| --- | --- |
| Flask | Web framework |
| PostgreSQL | Application database |
| psycopg | PostgreSQL driver |
| Requests | HTTP client |
| BeautifulSoup | HTML parsing |
| Bootstrap | UI styling |
| Gunicorn | Production WSGI server |
| uv | Dependency management |
| Ruff | Linting |

## Installation

```bash
git clone https://github.com/Korjick/python-project-83.git
cd python-project-83
```

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/page_analyzer
SECRET_KEY=your-secret-key
```

Install dependencies:

```bash
make install
```

Prepare the database:

```bash
make build
```

## Usage

Run the development server:

```bash
make dev
```

Run the production server locally:

```bash
make start
```

Run the linter:

```bash
make lint
```
