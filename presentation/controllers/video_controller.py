from datetime import datetime
from io import BytesIO
from flask import Flask, request, jsonify, render_template

import os
import base64
import mimetypes
import qrcode
import requests
import paths

@app.route("/api/upload-image", methods=["POST"])
def api_upload_image():
    """
    Riceve un'immagine dal telefono, la carica su Gemini File API,
    chiede la generazione del video e salva il risultato in static/generated.
    """

    if "image" not in request.files:
        return jsonify({"ok": False, "error": "Nessun file ricevuto"}), 400

    image_file = request.files["image"]
    prompt = request.form.get("prompt", "")

    if image_file.filename == "":
        return jsonify({"ok": False, "error": "File vuoto"}), 400

    filename = image_file.filename
    safe_name = filename.replace(" ", "_")
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    save_name = f"{timestamp}_{safe_name}"
    save_path = os.path.join(paths.Paths.UPLOAD_FOLDER(), save_name)
    image_file.save(save_path)

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
        CURRENT_VIDEO["updated_at"] = timestamp = TimeUtils._now_iso()

        return jsonify({"ok": True, "video_url": rel_url})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500
