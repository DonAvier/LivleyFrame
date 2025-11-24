from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class User:
    """Rappresenta un utente che interagisce con il sistema."""

    user_id: str
    email: str
    display_name: str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        if not self.user_id:
            raise ValueError("user_id obbligatorio")
        if not self.email:
            raise ValueError("email obbligatoria")
