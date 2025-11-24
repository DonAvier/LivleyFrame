from datetime import datetime
from paths import Paths

import os

class MediaFile:
    filename: str
    safe_name: int
    timestamp: str
    save_name: str
    save_path: str
    upload_ok: bool = False
    upload_message: str = ""
    image_file: any

    def __init__(self, request:any):
        if "image" not in request.files:
            self.upload_ok = False
            self.upload_message = "Nessun file ricevuto"

        image_file = request.files["image"]

        if image_file.filename == "":
            self.upload_ok = False
            self.upload_message = "File vuoto"

        self.filename = image_file.filename
        self.safe_name = image_file.filename.replace(" ", "_")
        self.timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        self.save_name = f"{self.timestamp}_{self.safe_name}"
        self.save_path = os.path.join(Paths.get_upload_folder_path(), self.save_name)

    def save(self):
        if(not self.upload_ok):
            return

        try:
            self.image_file.save(self.save_path)
            self.upload_ok = True
            self.upload_message = "File salvato con successo"
        except Exception as e:
            self.upload_ok = False
            self.upload_message = f"Errore nel salvataggio del file: {str(e)}"