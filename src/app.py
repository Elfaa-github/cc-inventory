"""API inventory sederhana (Flask + MySQL): satu entity Item, empat operasi CRUD."""
import logging
import re
import uuid
from datetime import datetime, timezone

import pymysql
from flask import Flask, jsonify, request

import db

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

app = Flask(__name__)
app.json.sort_keys = False  # urutan field mengikuti urutan yang kita susun

ID_PATTERN = re.compile(r"[A-Za-z0-9-]{1,64}")
MAX_TEXT_LENGTH = 255
MAX_QUANTITY = 2147483647  # batas tipe INT pada MySQL
COLUMNS = "id, name, category, quantity, location, updated_at"


def error(message, status):
    return jsonify({"error": message}), status


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def validate_item(payload):
    """Kembalikan (data, None) kalau valid, atau (None, pesan_error) kalau tidak."""
    if not isinstance(payload, dict):
        return None, "Body harus berupa JSON object"

    data = {}
    for field in ("name", "category", "quantity", "location"):
        value = payload.get(field)
        if field == "quantity":
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                return None, "Field 'quantity' wajib bilangan bulat minimal 0"
            if value > MAX_QUANTITY:
                return None, f"Field 'quantity' maksimal {MAX_QUANTITY}"
        else:
            if not isinstance(value, str) or not value.strip():
                return None, f"Field '{field}' wajib diisi (teks)"
            value = value.strip()
            if len(value) > MAX_TEXT_LENGTH:
                return None, f"Field '{field}' maksimal {MAX_TEXT_LENGTH} karakter"
        data[field] = value
    return data, None


def run_query(sql, params=()):
    """Jalankan satu query. Kembalikan (rowcount, baris_pertama)."""
    conn = db.get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.rowcount, cur.fetchone()
    finally:
        conn.close()


@app.get("/health")
def health():
    """Cek aplikasi dan koneksi database (untuk tes konektivitas)."""
    try:
        run_query("SELECT 1")
    except (pymysql.MySQLError, OSError, RuntimeError):
        app.logger.exception("Health check gagal")
        return jsonify({"status": "error", "database": "unreachable"}), 503
    return jsonify({"status": "ok", "database": "ok"}), 200


@app.post("/items")
def create_item():
    data, problem = validate_item(request.get_json(force=True, silent=True))
    if problem:
        return error(problem, 400)

    item = {"id": str(uuid.uuid4()), **data, "updated_at": now_iso()}
    run_query(
        f"INSERT INTO items ({COLUMNS}) VALUES (%s, %s, %s, %s, %s, %s)",
        (item["id"], item["name"], item["category"], item["quantity"],
         item["location"], item["updated_at"]),
    )
    app.logger.info("Item dibuat: %s", item["id"])
    return jsonify(item), 201


@app.get("/items/<item_id>")
def read_item(item_id):
    if not ID_PATTERN.fullmatch(item_id):
        return error("ID tidak valid", 400)
    _, row = run_query(f"SELECT {COLUMNS} FROM items WHERE id = %s", (item_id,))
    if row is None:
        return error("Item tidak ditemukan", 404)
    return jsonify(row), 200


@app.put("/items/<item_id>")
def update_item(item_id):
    if not ID_PATTERN.fullmatch(item_id):
        return error("ID tidak valid", 400)
    data, problem = validate_item(request.get_json(force=True, silent=True))
    if problem:
        return error(problem, 400)

    item = {"id": item_id, **data, "updated_at": now_iso()}
    matched, _ = run_query(
        "UPDATE items SET name = %s, category = %s, quantity = %s, "
        "location = %s, updated_at = %s WHERE id = %s",
        (item["name"], item["category"], item["quantity"], item["location"],
         item["updated_at"], item_id),
    )
    if matched == 0:
        return error("Item tidak ditemukan", 404)
    app.logger.info("Item diubah: %s", item_id)
    return jsonify(item), 200


@app.delete("/items/<item_id>")
def delete_item(item_id):
    if not ID_PATTERN.fullmatch(item_id):
        return error("ID tidak valid", 400)
    deleted, _ = run_query("DELETE FROM items WHERE id = %s", (item_id,))
    if deleted == 0:
        return error("Item tidak ditemukan", 404)
    app.logger.info("Item dihapus: %s", item_id)
    return jsonify({"message": "Item dihapus"}), 200


@app.errorhandler(404)
def not_found(_):
    return error("Not Found", 404)


@app.errorhandler(405)
def method_not_allowed(exc):
    response = jsonify({"error": "Method Not Allowed"})
    response.status_code = 405
    if exc.valid_methods:
        response.headers["Allow"] = ", ".join(exc.valid_methods)
    return response


@app.errorhandler(pymysql.MySQLError)
def database_error(_):
    app.logger.exception("Kesalahan database")
    return error("Kesalahan database", 500)


@app.errorhandler(500)
def server_error(_):
    return error("Internal Server Error", 500)
