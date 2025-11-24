from domain.service.file_manager import FileManager
from paths import Paths


class ImageManager(FileManager):
    """Manager specifico per le immagini."""

    def __init__(self):
        super().__init__(Paths.get_upload_folder_path(), "uploads")
