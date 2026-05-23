import pymssql
from decimal import Decimal
from config import DB_SERVER, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD


def _get_conn():
    return pymssql.connect(
        server=DB_SERVER,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        timeout=30,
        charset="UTF-8",
    )


def _serialize(row: dict) -> dict:
    result = {}
    for k, v in row.items():
        if isinstance(v, Decimal):
            result[k] = float(v)
        elif isinstance(v, str):
            result[k] = v.strip()
        else:
            result[k] = v
    return result


def query_db(sql: str, args: list = None) -> list[dict]:
    conn = _get_conn()
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(sql, args or [])
        return [_serialize(r) for r in cursor.fetchall()]
    finally:
        conn.close()
