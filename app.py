from flask import Flask, render_template, request, send_from_directory
from openai import OpenAI
import os
import uuid

app = Flask(__name__)
client = OpenAI()

AUDIO_DIR = "static/audio"

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/tts", methods=["POST"])
def tts():
    text = request.form.get("text")
    voice = request.form.get("voice")
    language = request.form.get("language")

    if not text:
        return "Texto vacío", 400

    if len(text) > 500:
        return "Máximo 500 caracteres", 400

    # 🔹 TRADUCCIÓN
    if language != "auto":
        translation = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"Traduce este texto al idioma {language}"},
                {"role": "user", "content": text}
            ]
        )
        text = translation.choices[0].message.content

    # 🔹 GENERAR AUDIO
    filename = f"{uuid.uuid4()}.mp3"
    filepath = os.path.join(AUDIO_DIR, filename)

    with client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice=voice,
        input=text
    ) as response:
        response.stream_to_file(filepath)

    return render_template("index.html", audio_file=filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
