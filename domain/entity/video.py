from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Video:
    """Entità dominio che rappresenta il video generato."""

    url: str
    version: int = 0
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def touch(self) -> None:
        """Aggiorna il timestamp quando il video viene rigenerato."""
        self.updated_at = datetime.utcnow()
        self.version += 1
