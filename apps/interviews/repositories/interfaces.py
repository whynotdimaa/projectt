from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, Optional

from ..dto import (
    InterviewCreateDTO,
    InterviewDTO,
    InterviewEvaluateDTO,
    InterviewFilterDTO,
)


class IInterviewRepository(ABC):
    @abstractmethod
    def get_by_id(self, interview_id: int) -> Optional[InterviewDTO]: ...

    @abstractmethod
    def list(self, filters: InterviewFilterDTO) -> Iterable[InterviewDTO]: ...

    @abstractmethod
    def add(self, data: InterviewCreateDTO) -> InterviewDTO: ...

    @abstractmethod
    def evaluate(self, interview_id: int, data: InterviewEvaluateDTO) -> InterviewDTO: ...

    @abstractmethod
    def delete(self, interview_id: int) -> None: ...
