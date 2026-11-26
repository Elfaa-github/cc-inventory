#!/usr/bin/env bash
# Tes CRUD otomatis terhadap API. Mencetak PASS/FAIL beserta kode status HTTP.
# Pemakaian: ./scripts/smoke-test.sh http://<alamat>:8080
set -u

URL="${1:-}"
if [ -z "$URL" ]; then
  echo "Pemakaian: $0 http://<alamat>:8080"
  exit 2
fi
URL="${URL%/}"
FAILED=0

# request <method> <path> [json-body] -> mengisi CODE dan BODY
request() {
  local method="$1" path="$2" body="${3:-}" resp
  if [ -n "$body" ]; then
    resp=$(curl -s -w $'\n%{http_code}' -X "$method" "$URL$path" \
      -H "Content-Type: application/json" -d "$body")
  else
    resp=$(curl -s -w $'\n%{http_code}' -X "$method" "$URL$path")
  fi
  CODE="${resp##*$'\n'}"
  BODY="${resp%$'\n'*}"
}

# check <nama> <kode-harapan>
check() {
  if [ "$CODE" = "$2" ]; then
    echo "PASS  $1 (HTTP $CODE)"
  else
    echo "FAIL  $1 (harapan $2, dapat $CODE)"
    FAILED=1
  fi
  echo "      $BODY" | tr -d '\n'; echo
}

request GET /health;                                   check "GET /health" 200

request POST /items '{"name":"Contoh barang","category":"Contoh","quantity":3,"location":"Gudang A"}'
check "Create item (201)" 201
ID=$(echo "$BODY" | sed -n 's/.*"id": *"\([^"]*\)".*/\1/p')
if [ -z "$ID" ]; then echo "FAIL  ID item tidak ditemukan pada respons Create"; exit 1; fi

request GET "/items/$ID";                              check "Read item (200)" 200

request PUT "/items/$ID" '{"name":"Contoh barang","category":"Contoh","quantity":7,"location":"Gudang A"}'
check "Update item (200)" 200
echo "$BODY" | grep -Eq '"quantity": ?7' || { echo "FAIL  quantity tidak berubah menjadi 7"; FAILED=1; }

request POST /items '{"name":"Contoh barang","quantity":1,"location":"Gudang A"}'
check "Input tidak valid, tanpa category (400)" 400

request DELETE "/items/$ID";                           check "Delete item (200)" 200
request GET "/items/$ID";                              check "Read setelah dihapus (404)" 404

if [ "$FAILED" -eq 0 ]; then echo "SEMUA TES LULUS"; else echo "ADA TES YANG GAGAL"; fi
exit "$FAILED"
