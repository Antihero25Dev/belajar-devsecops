"""Modul backend autentikasi Flask dengan antarmuka web interaktif."""

import sqlite3
from functools import wraps

from flask import Flask, render_template, request
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

DATABASE = "users.db"


def get_db_connection():
    """Membuka koneksi ke database SQLite."""
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    """Inisialisasi basis data dan membuat data pengguna awal."""
    with get_db_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL
            )
            """
        )

        admin_password = generate_password_hash("supersecret")

        connection.execute(
            """
            INSERT OR IGNORE INTO users (username, password)
            VALUES (?, ?)
            """,
            ("admin", admin_password),
        )

        connection.commit()


@app.route("/", methods=["GET", "POST"])
def index():
    """Menampilkan formulir login dan memproses autentikasi."""
    message = None
    status_class = None

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            message = "Username dan password wajib diisi."
            status_class = "danger"
        else:
            with get_db_connection() as connection:
                user = connection.execute(
                    """
                    SELECT username, password
                    FROM users
                    WHERE username = ?
                    """,
                    (username,),
                ).fetchone()

            if user and check_password_hash(user["password"], password):
                message = "Login Berhasil! Selamat datang."
                status_class = "success"
            else:
                message = "Login Gagal! Kredensial tidak valid."
                status_class = "danger"

    return render_template(
        "index.html",
        message=message,
        status_class=status_class,
    )


@app.route("/mahasiswa")
def mahasiswa():
    """Menampilkan nama mahasiswa yang diberikan melalui parameter URL."""
    nama = request.args.get("nama", "").strip()

    if not nama:
        return "Nama mahasiswa belum diberikan.", 400

    if len(nama) > 100:
        return "Nama mahasiswa terlalu panjang.", 400

    return "Fitur mahasiswa berhasil dibuat"


if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000)
