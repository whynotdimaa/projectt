from ..repositories.interview_repository import InterviewRepository
from .interview_service import InterviewService


def get_interview_service() -> InterviewService:
    return InterviewService(repo=InterviewRepository())
