from page_analyzer.db import get_connection


def create_url(name, created_at):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO urls (name, created_at) VALUES (%s, %s) RETURNING id",
                (name, created_at),
            )
            row = cursor.fetchone()
            return row["id"]


def get_url_by_name(name):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, name, created_at FROM urls WHERE name = %s", (name,))
            return cursor.fetchone()


def get_url_by_id(url_id):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id, name, created_at FROM urls WHERE id = %s",
                (url_id,),
            )
            return cursor.fetchone()


def get_urls():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    urls.id,
                    urls.name,
                    urls.created_at,
                    checks.created_at AS last_check_created_at,
                    checks.status_code AS last_check_status_code
                FROM urls
                LEFT JOIN LATERAL (
                    SELECT created_at, status_code
                    FROM url_checks
                    WHERE url_id = urls.id
                    ORDER BY id DESC
                    LIMIT 1
                ) AS checks ON TRUE
                ORDER BY urls.id DESC
                """,
            )
            return cursor.fetchall()


def create_url_check(url_id, status_code, h1, title, description, created_at):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO url_checks (
                    url_id,
                    status_code,
                    h1,
                    title,
                    description,
                    created_at
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (url_id, status_code, h1, title, description, created_at),
            )


def get_url_checks(url_id):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, url_id, status_code, h1, title, description, created_at
                FROM url_checks
                WHERE url_id = %s
                ORDER BY id DESC
                """,
                (url_id,),
            )
            return cursor.fetchall()
