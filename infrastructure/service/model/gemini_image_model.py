import base64
import mimetypes
import os
from typing import Tuple

import requests

from config import GEMINI_API_KEY, GEMINI_MODEL, GEMINI_BASE_URL
from domain.entity.abstraction.iimage_model import IImageModel
from domain.entity.media_file import MediaFile


class GeminiImageModel(IImageModel):
    """Adapter per invocare la Gemini File API e generare un video dalle immagini."""

    def __init__(self, prompt: str | None = None):
        self.media_file: MediaFile | None = None
        self.prompt = prompt or "Create a short, gentle, realistic motion video based on this photo."

    def ImportMedia(self, media_file: MediaFile):
        if not isinstance(media_file, MediaFile):
            raise TypeError("media_file deve essere un'istanza di MediaFile")
        self.media_file = media_file

        # Se il file non è ancora stato salvato, effettua il salvataggio tramite l'entità
        if not media_file.upload_ok:
            media_file.save()
        if not media_file.upload_ok:
            raise ValueError(media_file.upload_message)

    def _upload_file_to_gemini(self, image_path: str) -> Tuple[str, str]:
        if not GEMINI_API_KEY or GEMINI_API_KEY == "PASTE_YOUR_API_KEY_HERE":
            raise RuntimeError("GEMINI_API_KEY non impostata in config.py")

        endpoint = f"{GEMINI_BASE_URL}/files?key={GEMINI_API_KEY}"

        mime_type, _ = mimetypes.guess_type(image_path)
        if mime_type is None:
            mime_type = "image/jpeg"

        with open(image_path, "rb") as handler:
            files = {
                "file": (os.path.basename(image_path), handler, mime_type),
            }
            data = {"file_purpose": "GENERATIVE"}
            resp = requests.post(endpoint, files=files, data=data, timeout=60)

        if resp.status_code >= 300:
            raise RuntimeError(f"Errore upload file a Gemini: {resp.status_code} {resp.text}")

        payload = resp.json()
        file_obj = payload.get("file") or payload
        file_name = file_obj.get("name")
        if not file_name:
            raise RuntimeError(f"Risposta Gemini senza 'file.name': {payload}")
        return file_name, mime_type

    def _generate_video(self, file_name: str, mime_type: str) -> bytes:
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
                        {"text": self.prompt},
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

        payload = resp.json()
        try:
            candidates = payload["candidates"]
            parts = candidates[0]["content"]["parts"]
            inline_data = parts[0].get("inline_data") or parts[-1].get("inline_data")
            if not inline_data:
                raise KeyError("inline_data mancante")

            encoded_video = inline_data["data"]
            return base64.b64decode(encoded_video)
        except Exception as exc:  # pragma: no cover - logging placeholder
            raise RuntimeError(
                f"Impossibile estrarre video dalla risposta Gemini: {exc}; risposta: {payload}"
            ) from exc

    def RunModel(self) -> bytes:
        if self.media_file is None:
            raise RuntimeError("Nessun media importato. Chiama ImportMedia prima di RunModel().")

        file_name, mime_type = self._upload_file_to_gemini(self.media_file.save_path)
        return self._generate_video(file_name, mime_type)
