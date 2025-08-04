class NeteaseApiException(Exception):
    def __init__(self, message: str, code: int):
        super().__init__(message + f" (code: {str(code)})")
        self.code = code
