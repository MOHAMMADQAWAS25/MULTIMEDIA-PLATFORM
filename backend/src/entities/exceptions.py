class InkFigError(Exception):
    code = "inkfig_error"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class WorkNotFoundError(InkFigError):
    code = "work_not_found"


class InvalidWorkStatusTransitionError(InkFigError):
    code = "invalid_work_status_transition"
