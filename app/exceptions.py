from typing import Any, Optional, Dict

from fastapi import status
from fastapi import HTTPException
from starlette.responses import JSONResponse

from app.schemas import ErrorSchema


async def http_exception_handler(request, exc):
    content = ErrorSchema(status='Bad request', message=exc.detail, statusCode=exc.status_code).model_dump(mode='json')
    return JSONResponse(content, status_code=exc.status_code)


class AuthError(HTTPException):
    def __init__(
        self, detail: Any = None, headers: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(status.HTTP_401_UNAUTHORIZED, detail, headers)
        
class RegistrationError(HTTPException):
    def __init__(
        self, detail: Any = None, headers: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(status.HTTP_400_BAD_REQUEST, detail, headers)


class NotFoundError(HTTPException):
    def __init__(
        self, detail: Any = None, headers: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(status.HTTP_404_NOT_FOUND, detail, headers)