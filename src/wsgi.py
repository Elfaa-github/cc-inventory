"""Titik masuk gunicorn: siapkan tabel (menunggu database siap), lalu sajikan app."""
import db
from app import app  # noqa: F401  (dipakai gunicorn sebagai wsgi:app)

db.init_db()
