import os
import base64
import mimetypes
from datetime import datetime
from io import BytesIO

import requests
from domain.entity.media_file import MediaFile
from flask import Flask, request, jsonify, render_template

import qrcode

from config import GEMINI_API_KEY, GEMINI_MODEL, GEMINI_BASE_URL, VIDEO_DURATION_SECONDS

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
GENERATED_FOLDER = os.path.join(BASE_DIR, "static", "generated")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(GENERATED_FOLDER, exist_ok=True)

# Stato del video corrente mostrato dalla cornice
CURRENT_VIDEO = {
    "url": None,
    "version": 0,
    "updated_at": None,
}


def _now_iso():
    return datetime.utcnow().isoformat()


@app.route("/")
def index():
    return render_template("frame.html")


@app.route("/frame")
def frame():
    return render_template("frame.html")


@app.route("/control")
def control():
    return render_template("control.html")

@app.route("/control-test")
def control_test():
    return render_template("control_test.html")

@app.route("/api/current-video")
def api_current_video():
    has_video = CURRENT_VIDEO["url"] is not None
    return jsonify(
        {
            "url": CURRENT_VIDEO["url"],
            "version": CURRENT_VIDEO["version"],
            "updated_at": CURRENT_VIDEO["updated_at"],
            "has_video": has_video,
        }
    )


@app.route("/api/qr")
def api_qr():
    """
    Genera un QR che punta alla pagina di controllo (/control) raggiungibile
    dal telefono sulla stessa rete.
    """
    # request.host contiene es. "192.168.1.42:5000"
    host = request.host
    control_url = f"http://{host}/control"

    qr = qrcode.QRCode(box_size=8, border=2)
    qr.add_data(control_url)
    qr.make()
    img = qr.make_image(fill_color="black", back_color="white")

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")

    return jsonify({"qr": encoded, "url": control_url})


def upload_file_to_gemini(image_path: str) -> str:
    """
    Carica il file immagine alla Gemini File API e ritorna il file name / URI.
    Documentazione (potrebbe cambiare): https://ai.google.dev/gemini-api/docs
    """
    if not GEMINI_API_KEY or GEMINI_API_KEY == "PASTE_YOUR_API_KEY_HERE":
        raise RuntimeError("GEMINI_API_KEY non impostata in config.py")

    endpoint = f"{GEMINI_BASE_URL}/files?key={GEMINI_API_KEY}"

    mime_type, _ = mimetypes.guess_type(image_path)
    if mime_type is None:
        mime_type = "image/jpeg"

    with open(image_path, "rb") as f:
        files = {
            "file": (os.path.basename(image_path), f, mime_type),
        }
        data = {"file_purpose": "GENERATIVE"}
        resp = requests.post(endpoint, files=files, data=data, timeout=60)

    if resp.status_code >= 300:
        raise RuntimeError(f"Errore upload file a Gemini: {resp.status_code} {resp.text}")

    j = resp.json()
    # struttura tipica: {"file": {"name": "files/xxx", ...}}
    file_obj = j.get("file") or j
    file_name = file_obj.get("name")
    if not file_name:
        raise RuntimeError(f"Risposta Gemini senza 'file.name': {j}")

    return file_name, mime_type


def generate_video_with_gemini(file_name: str, mime_type: str, prompt: str) -> bytes:
    """
    Chiede a Gemini di generare un breve video MP4 a partire dal file caricato.
    Usa generateContent con response_mime_type=video/mp4.

    ATTENZIONE: la struttura esatta della risposta potrebbe variare con aggiornamenti
    dell'API; questo è un prototipo basato sulla documentazione v1beta.
    """
    if not prompt:
        prompt = "Create a short, gentle, realistic motion video based on this photo."

    endpoint = f"{GEMINI_BASE_URL}/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"

    body = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "file_data": {
                            "file_uri": file_name,
                            "mime_type": mime_type,
                        }
                    },
                    {"text": prompt},
                ],
            }
        ],
        "generationConfig": {
            "response_mime_type": "video/mp4",
        },
    }

    resp = requests.post(endpoint, json=body, timeout=600)

    if resp.status_code >= 300:
        raise RuntimeError(f"Errore generateContent Gemini: {resp.status_code} {resp.text}")

    j = resp.json()

    # L'output video tende ad arrivare come inline_data base64 in candidates[0].content.parts[0]
    try:
        candidates = j["candidates"]
        parts = candidates[0]["content"]["parts"]
        inline_data = parts[0].get("inline_data") or parts[-1].get("inline_data")
        if not inline_data:
            raise KeyError("inline_data mancante")
        b64_video = inline_data["data"]
        video_bytes = base64.b64decode(b64_video)
        return video_bytes
    except Exception as e:
        raise RuntimeError(f"Impossibile estrarre video dalla risposta Gemini: {e}; risposta: {j}")


@app.route("/api/upload-image", methods=["POST"])
def api_upload_image():
    """
    Riceve un'immagine dal telefono, la carica su Gemini File API,
    chiede la generazione del video e salva il risultato in static/generated.
    """

    prompt = request.form.get("prompt", "")

    media = MediaFile(request)
    media.save()

    try:
        # 1) upload file to Gemini File API
        file_name, mime_type = upload_file_to_gemini(save_path)

        # 2) ask Gemini to generate video
        video_bytes = generate_video_with_gemini(file_name, mime_type, prompt)

        # 3) save video locally
        video_filename = f"video_{CURRENT_VIDEO['version'] + 1}_{timestamp}.mp4"
        video_path = os.path.join(GENERATED_FOLDER, video_filename)
        with open(video_path, "wb") as vf:
            vf.write(video_bytes)

        rel_url = f"/static/generated/{video_filename}"

        # 4) update state
        CURRENT_VIDEO["url"] = rel_url
        CURRENT_VIDEO["version"] += 1
        CURRENT_VIDEO["updated_at"] = _now_iso()

        return jsonify({"ok": True, "video_url": rel_url})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


if __name__ == "__main__":
    # Ascolta su tutte le interfacce per permettere l'accesso dalla LAN (telefono / tablet)
    app.run(host="0.0.0.0", port=5000, debug=True)
