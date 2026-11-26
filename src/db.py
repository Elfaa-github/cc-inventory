"""Akses database MySQL: konfigurasi, koneksi, dan pembuatan tabel."""
import os
import time

import pymysql
from pymysql.constants import CLIENT
from pymysql.cursors import DictCursor

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS items (
    id         VARCHAR(64)  NOT NULL PRIMARY KEY,
    name       VARCHAR(255) NOT NULL,
    category   VARCHAR(255) NOT NULL,
    quantity   INT          NOT NULL,
    location   VARCHAR(255) NOT NULL,
    updated_at VARCHAR(32)  NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
"""


def _config():
    """Baca konfigurasi dari environment variable. Tidak ada password bawaan."""
    try:
        return {
            "host": os.environ.get("DB_HOST", "db"),
            "port": int(os.environ.get("DB_PORT", "3306")),
            "user": os.environ["DB_USER"],
            "password": os.environ["DB_PASSWORD"],
            "database": os.environ["DB_NAME"],
        }
    except KeyError as err:
        raise RuntimeError(f"Environment variable {err} belum diatur") from err


def get_connection():
    """Buka koneksi baru. FOUND_ROWS membuat rowcount = jumlah baris yang cocok."""
    return pymysql.connect(
        **_config(),
        charset="utf8mb4",
        cursorclass=DictCursor,
        autocommit=True,
        connect_timeout=5,
        client_flag=CLIENT.FOUND_ROWS,
    )


def init_db(retries=30, delay=2):
    """Buat tabel items. Mengulang sampai database siap menerima koneksi."""
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            conn = get_connection()
            try:
                with conn.cursor() as cur:
                    cur.execute(CREATE_TABLE_SQL)
            finally:
                conn.close()
            print("Database siap.", flush=True)
            return
        except (pymysql.MySQLError, OSError) as err:
            last_error = err
            print(f"Menunggu database ({attempt}/{retries}): {err}", flush=True)
            time.sleep(delay)
    raise RuntimeError(f"Database tidak dapat dihubungi: {last_error}")
