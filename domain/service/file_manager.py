import os
from domain.entity.media_file import MediaFile
from domain.service.abstraction.ifile_manager import IFileManager
from paths import Paths


class FileManager(IFileManager):
    """Implementazione base che salva su filesystem locale."""

    def __init__(self, base_path: str, public_root: str):
        self.base_path = base_path
        self.public_root = public_root.rstrip("/")
        Paths.ensure_directories([self.base_path])

    def save_media(self, media_file: MediaFile) -> str:
        if not isinstance(media_file, MediaFile):
            raise TypeError("media_file deve essere un MediaFile")

        media_file.save()
        if not media_file.upload_ok:
            raise ValueError(media_file.upload_message)
        return media_file.save_path

    def save_bytes(self, content: bytes, filename: str) -> str:
        if not filename:
            raise ValueError("filename mancante")
        Paths.ensure_directories([self.base_path])
        target = os.path.join(self.base_path, filename)
        with open(target, "wb") as handler:
            handler.write(content)
        return target

    def get_public_path(self, filename: str) -> str:
        if not filename:
            raise ValueError("filename mancante")
        return f"{self.public_root}/{filename}"
