"""
Доменні виключення. НЕ залежать від HTTP / DRF.
API-шар сам мапить їх на HTTP-коди (Крок 3).
"""


class DomainError(Exception):
    """Базове виключення доменного шару."""


class NotFoundError(DomainError):
    """Сутність не знайдена."""


class ValidationError(DomainError):
    """Порушення доменних інваріантів (напр., неприпустимий перехід статусу)."""


class ConflictError(DomainError):
    """Конфлікт стану (напр., дублікат email)."""
