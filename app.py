from flask import Flask, render_template, request, redirect, session
from openai import OpenAI
import sqlite3
import os
import uuid

app = Flask(__name__)
app.secret_key = "secret123"

client = OpenAI()

AUDIO_DIR = "static/audio"

# -----------------------
# BASE DE DATOS
# -----------------------
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT,
        tipo TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# -----------------------
# HOME
# -----------------------
@app.route("/")
def index():
    if "audios" not in session:
        session["audios"] = 0

    premium = False
    user = None

    if "user_id" in session:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT username, tipo FROM users WHERE id=?", (session["user_id"],))
        user = cursor.fetchone()
        conn.close()

        if user:
            if user[1] == "premium":
                premium = True

    return render_template("index.html",
                           premium=premium,
                           audios=session["audios"],
                           user=user)

# -----------------------
# REGISTER
# -----------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("INSERT INTO users (username, password, tipo) VALUES (?, ?, ?)",
                       (username, password, "free"))

        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")

# -----------------------
# LOGIN
# -----------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("SELECT id, tipo FROM users WHERE username=? AND password=?",
                       (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session["user_id"] = user[0]
            return redirect("/")
        else:
            error = "Usuario o contraseña incorrectos"

    return render_template("login.html", error=error)

# -----------------------
# LOGOUT
# -----------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# -----------------------
# SIMULAR STRIPE (PREMIUM)
# -----------------------
@app.route("/upgrade")
def upgrade():
    if "user_id" not in session:
        return redirect("/login")

    return redirect("/pago")
    
@app.route("/pago")
def pago():
    return render_template("pago.html")


@app.route("/confirmar_pago")
def confirmar_pago():
    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("UPDATE users SET tipo='premium' WHERE id=?", (session["user_id"],))

    conn.commit()
    conn.close()

    return redirect("/")

# -----------------------
# TTS
# -----------------------
@app.route("/tts", methods=["POST"])
def tts():
    text = request.form.get("text")
    voice = request.form.get("voice")
    language = request.form.get("language")

    premium = False

    if "user_id" in session:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT tipo FROM users WHERE id=?", (session["user_id"],))
        user = cursor.fetchone()
        conn.close()

        if user and user[0] == "premium":
            premium = True

    audios = session.get("audios", 0)

    # 🔒 RESTRICCIONES
    if not premium:
        if len(text) > 500:
            return "Máximo 500 caracteres"

        if audios >= 3:
            return render_template("index.html",
                                   error="Límite alcanzado. Suscribete al Modelo Premium",
                                   premium=premium,
                                   audios=audios)

        if language != "auto":
            return render_template("index.html",
                                   error="Función premium 🔒",
                                   premium=premium,
                                   audios=audios)

    # TRADUCCIÓN
    if language != "auto":
        translation = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"Traduce al idioma {language}"},
                {"role": "user", "content": text}
            ]
        )
        text = translation.choices[0].message.content

    filename = f"{uuid.uuid4()}.mp3"
    filepath = os.path.join(AUDIO_DIR, filename)

    with client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice=voice,
        input=text
    ) as response:
        response.stream_to_file(filepath)

    session["audios"] = audios + 1

    return render_template("index.html",
                       audio_file=filename,
                       premium=premium,
                       audios=session["audios"])


if __name__ == "__main__":
    app.run()