from abc import ABC, abstractmethod
from domain.entity.media_file import MediaFile


class IFileManager(ABC):
    """Contratto per i manager di salvataggio file (immagini e video)."""

    @abstractmethod
    def save_media(self, media_file: MediaFile) -> str:
        """Salva un file caricato e restituisce il percorso finale."""
        raise NotImplementedError

    @abstractmethod
    def save_bytes(self, content: bytes, filename: str) -> str:
        """Salva un contenuto binario e restituisce il percorso finale."""
        raise NotImplementedError

    @abstractmethod
    def get_public_path(self, filename: str) -> str:
        """Restituisce il percorso pubblico relativo da esporre all'utente."""
        raise NotImplementedError
