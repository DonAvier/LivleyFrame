class TimeUtils:

    @staticmethod
    def _now_iso():
        return datetime.utcnow().isoformat()