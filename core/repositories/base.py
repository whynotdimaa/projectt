"""
Generic Repository interface (Крок 1 — лише контракт).
Конкретні репозиторії з'являться у Кроці 2.

Сервіси будуть залежати ТІЛЬКИ від цих абстракцій (DIP з SOLID).
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, Iterable, Optional, TypeVar

T = TypeVar("T")  # pragma: no cover
ID = TypeVar("ID")  # pragma: no cover


class IRepository(ABC, Generic[T, ID]):  # pragma: no cover
    @abstractmethod
    def get_by_id(self, entity_id: ID) -> Optional[T]: ...

    @abstractmethod
    def list(self, **filters) -> Iterable[T]: ...

    @abstractmethod
    def add(self, entity: T) -> T: ...

    @abstractmethod
    def update(self, entity: T) -> T: ...

    @abstractmethod
    def delete(self, entity_id: ID) -> None: ...
