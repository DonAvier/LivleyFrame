from domain.entity.abstraction import IImageModel
from domain.entity.media_file import MediaFile

from config import GEMINI_API_KEY, GEMINI_MODEL, GEMINI_BASE_URL, VIDEO_DURATION_SECONDS

class GeminiImageModel(IImageModel):

    def __init__(self):
        self.media_file: MediaFile | None = None



    def ImportMedia(self, media_file: MediaFile):
        if not isinstance(media_file, MediaFile):
            raise TypeError("media_file deve essere un'istanza di MediaFile")

        self.media_file = media_file
        print(f"[Gemini] Media importato: {media_file.path if hasattr(media_file, 'path') else media_file}")

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


    def RunModel(self):
        if self.media_file is None:
            raise RuntimeError("Nessun media importato. Chiama ImportMedia prima di RunModel().")

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
