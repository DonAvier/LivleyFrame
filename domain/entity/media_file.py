from __future__ import annotations

from datetime import datetime
import os

from paths import Paths


class MediaFile:
    filename: str
    safe_name: str
    timestamp: str
    save_name: str
    save_path: str
    upload_ok: bool
    upload_message: str
    image_file: any

    def __init__(self, request: any):
        self.upload_ok = True
        self.upload_message = ""
        self.image_file = None

        if "image" not in request.files:
            self.upload_ok = False
            self.upload_message = "Nessun file ricevuto"
            return

        image_file = request.files["image"]
        if image_file.filename == "":
            self.upload_ok = False
            self.upload_message = "File vuoto"
            return

        self.image_file = image_file
        self.filename = image_file.filename
        self.safe_name = image_file.filename.replace(" ", "_")
        self.timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        self.save_name = f"{self.timestamp}_{self.safe_name}"
        self.save_path = os.path.join(Paths.get_upload_folder_path(), self.save_name)

    @property
    def path(self) -> str:
        return self.save_path

    def save(self) -> None:
        if not self.upload_ok or not self.image_file:
            return

        Paths.ensure_directories([Paths.get_upload_folder_path()])
        try:
            self.image_file.save(self.save_path)
            self.upload_ok = True
            self.upload_message = "File salvato con successo"
        except Exception as exc:  # pragma: no cover - logging placeholder
            self.upload_ok = False
            self.upload_message = f"Errore nel salvataggio del file: {exc}"
