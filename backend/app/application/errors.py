class AppError(Exception):
    def __init__(
        self, *, code: str, message: str, status_code: int, details: object = None
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details


class ValidationAppError(AppError):
    def __init__(
        self, *, code: str = "VALIDATION_ERROR", message: str, details: object = None
    ) -> None:
        super().__init__(code=code, message=message, status_code=400, details=details)


class NotFoundAppError(AppError):
    def __init__(
        self, *, code: str = "NOT_FOUND", message: str, details: object = None
    ) -> None:
        super().__init__(code=code, message=message, status_code=404, details=details)


class LLMUnavailableError(AppError):
    def __init__(
        self,
        *,
        message: str = "No se pudo obtener respuesta del modelo local",
        details: object = None,
    ) -> None:
        super().__init__(
            code="OLLAMA_UNAVAILABLE",
            message=message,
            status_code=503,
            details=details,
        )
