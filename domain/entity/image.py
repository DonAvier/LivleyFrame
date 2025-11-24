from dataclasses import dataclass
from datetime import datetime


@dataclass
class Image:
    """Entità dominio che rappresenta una foto caricata dall'utente."""

    path: str
    uploaded_at: datetime
    prompt: str | None = None

    def __post_init__(self) -> None:
        if not self.path:
            raise ValueError("path immagine mancante")
