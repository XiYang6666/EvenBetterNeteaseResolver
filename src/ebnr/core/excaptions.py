class NeteaseApiException(Exception):
    def __init__(self, message: str, code: int, msg: str | None = None):
        super().__init__(
            f"{message} (code: {code}{f', message: {msg}' if msg else ''})"
        )
        self.code = code
