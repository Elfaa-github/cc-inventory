"""inventory-handler: API CRUD satu entity (Item) di AWS Lambda + Function URL, data disimpan di S3.

Satu Item = satu file JSON di S3 dengan key "items/{id}.json".
Nama bucket dibaca dari environment variable BUCKET_NAME (diatur di konfigurasi Lambda).
"""
import base64
import json
import logging
import os
import re
import uuid
from datetime import datetime, timezone

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client("s3")

# id dipakai sebagai bagian key S3, jadi dibatasi huruf/angka/tanda hubung saja
ID_PATTERN = re.compile(r"^[A-Za-z0-9-]{1,64}$")
NOT_FOUND_CODES = ("404", "NoSuchKey", "NotFound")


def response(status, body):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


def bucket_name():
    return os.environ["BUCKET_NAME"]


def item_key(item_id):
    return f"items/{item_id}.json"


def item_exists(item_id):
    try:
        s3.head_object(Bucket=bucket_name(), Key=item_key(item_id))
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] in NOT_FOUND_CODES:
            return False
        raise


def save_item(item):
    s3.put_object(
        Bucket=bucket_name(),
        Key=item_key(item["id"]),
        Body=json.dumps(item).encode("utf-8"),
        ContentType="application/json",
    )


def load_item(item_id):
    """Return dict item, atau None kalau tidak ada."""
    try:
        obj = s3.get_object(Bucket=bucket_name(), Key=item_key(item_id))
    except ClientError as e:
        if e.response["Error"]["Code"] in NOT_FOUND_CODES:
            return None
        raise
    return json.loads(obj["Body"].read())


def parse_item(event):
    """Baca body JSON dan cek field. Return (data, pesan_error)."""
    raw = event.get("body")
    try:
        if raw and event.get("isBase64Encoded"):
            raw = base64.b64decode(raw).decode("utf-8")
        data = json.loads(raw or "")
    except (TypeError, ValueError):
        return None, "Body harus berupa JSON yang valid"
    if not isinstance(data, dict):
        return None, "Body harus berupa objek JSON"

    for field in ("name", "category", "location"):
        if not isinstance(data.get(field), str) or not data[field].strip():
            return None, f"Field '{field}' wajib diisi (teks)"
    qty = data.get("quantity")
    if isinstance(qty, bool) or not isinstance(qty, int) or qty < 0:
        return None, "Field 'quantity' wajib bilangan bulat >= 0"

    return {
        "name": data["name"].strip(),
        "category": data["category"].strip(),
        "quantity": qty,
        "location": data["location"].strip(),
    }, None


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def not_found(item_id):
    return response(404, {"error": f"Item '{item_id}' tidak ditemukan"})


def create_item(event):
    data, error = parse_item(event)
    if error:
        return response(400, {"error": error})
    item = {"id": str(uuid.uuid4()), **data, "updated_at": now_iso()}
    save_item(item)
    return response(201, item)


def get_item(item_id):
    item = load_item(item_id)
    return response(200, item) if item else not_found(item_id)


def update_item(event, item_id):
    data, error = parse_item(event)
    if error:
        return response(400, {"error": error})
    if not item_exists(item_id):
        return not_found(item_id)
    item = {"id": item_id, **data, "updated_at": now_iso()}
    save_item(item)
    return response(200, item)


def delete_item(item_id):
    # delete_object di S3 tidak error kalau key tidak ada, jadi cek dulu supaya bisa balas 404
    if not item_exists(item_id):
        return not_found(item_id)
    s3.delete_object(Bucket=bucket_name(), Key=item_key(item_id))
    return response(200, {"message": f"Item '{item_id}' dihapus"})


def route(event):
    """Function URL tidak mengisi routeKey (selalu $default), jadi route dibaca dari method + path."""
    method = event.get("requestContext", {}).get("http", {}).get("method")
    parts = [p for p in event.get("rawPath", "").split("/") if p]

    if parts == ["items"]:
        if method == "POST":
            return create_item(event)
        return response(405, {"error": f"Method {method} tidak didukung untuk /items"})

    if len(parts) == 2 and parts[0] == "items":
        item_id = parts[1]
        if not ID_PATTERN.match(item_id):
            return response(400, {"error": "id tidak valid"})
        if method == "GET":
            return get_item(item_id)
        if method == "PUT":
            return update_item(event, item_id)
        if method == "DELETE":
            return delete_item(item_id)
        return response(405, {"error": f"Method {method} tidak didukung untuk /items/{{id}}"})

    return response(404, {"error": "Path tidak dikenali"})


def lambda_handler(event, context):
    try:
        return route(event)
    except Exception:
        # detail error masuk ke CloudWatch Logs; client hanya menerima pesan umum
        logger.exception("Error tidak terduga")
        return response(500, {"error": "Terjadi kesalahan di server"})
