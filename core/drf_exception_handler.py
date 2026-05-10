"""
Кастомний DRF exception handler.
Єдина точка, де доменні виключення транслюються у HTTP-відповіді.
Сервіси/репо НЕ знають про DRF і HTTP-коди.
"""
from __future__ import annotations

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_default_handler

from .exceptions import ConflictError, DomainError, NotFoundError, ValidationError


_DOMAIN_TO_HTTP = (
    (NotFoundError, status.HTTP_404_NOT_FOUND),
    (ValidationError, status.HTTP_400_BAD_REQUEST),
    (ConflictError, status.HTTP_409_CONFLICT),
)


def custom_exception_handler(exc, context):
    # 1) спочатку доменні
    for exc_cls, http_code in _DOMAIN_TO_HTTP:
        if isinstance(exc, exc_cls):
            return Response({"detail": str(exc)}, status=http_code)

    # 2) generic DomainError -> 400
    if isinstance(exc, DomainError):
        return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    # 3) усе інше — стандартний DRF-handler
    return drf_default_handler(exc, context)
