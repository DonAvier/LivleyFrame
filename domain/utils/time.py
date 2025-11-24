from datetime import datetime


class TimeUtils:
    @staticmethod
    def now_iso() -> str:
        return datetime.utcnow().isoformat()
