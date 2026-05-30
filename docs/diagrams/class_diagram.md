# Class Diagram — HR Candidate Evaluation System

## Повна діаграма класів (архітектурні шари)

```mermaid
classDiagram

    %% ─── CORE ───────────────────────────────────────────────────────────────
    class IRepository~T, ID~ {
        <<interface>>
        +get_by_id(entity_id: ID) T
        +list(**filters) Iterable~T~
        +add(entity: T) T
        +update(entity: T) T
        +delete(entity_id: ID) None
    }

    class DomainError {
        +message: str
    }
    class NotFoundError
    class ValidationError
    class ConflictError

    DomainError <|-- NotFoundError
    DomainError <|-- ValidationError
    DomainError <|-- ConflictError

    %% ─── CANDIDATES ─────────────────────────────────────────────────────────
    class ICandidateRepository {
        <<interface>>
        +get_by_id(id) CandidateDTO
        +get_by_email(email) CandidateDTO
        +list(filters) Iterable~CandidateDTO~
        +add(data) CandidateDTO
        +update(id, data) CandidateDTO
        +update_status(id, status) CandidateDTO
        +delete(id) None
        +add_status_history(...) None
    }

    class CandidateRepository {
        +get_by_id(id) CandidateDTO
        +get_by_email(email) CandidateDTO
        +list(filters) Iterable~CandidateDTO~
        +add(data) CandidateDTO
        +update(id, data) CandidateDTO
        +update_status(id, status) CandidateDTO
        +delete(id) None
        +add_status_history(...) None
    }

    class CandidateService {
        -_repo: ICandidateRepository
        +__init__(repo: ICandidateRepository)
        +get(id) CandidateDTO
        +list(filters) Iterable~CandidateDTO~
        +create(data) CandidateDTO
        +update(id, data) CandidateDTO
        +delete(id) None
        +change_status(id, new_status, changed_by_id) CandidateDTO
    }

    ICandidateRepository <|.. CandidateRepository : implements
    IRepository <|-- ICandidateRepository
    CandidateService --> ICandidateRepository : depends on (DIP)

    %% ─── NOTIFICATIONS (Strategy Pattern) ───────────────────────────────────
    class INotificationStrategy {
        <<interface>>
        +name: str
        +send(message: NotificationMessage) None
    }

    class EmailStrategy {
        +name = "email"
        +send(message) None
    }

    class SlackStrategy {
        -_webhook_url: str
        +name = "slack"
        +send(message) None
    }

    class SMSStrategy {
        +name = "sms"
        +send(message) None
    }

    class NotificationStrategyFactory {
        <<factory>>
        +create(channel: str) INotificationStrategy
        +create_many(channels) list~INotificationStrategy~
        +available_channels() list~str~
    }

    class NotificationService {
        -_strategies: list~INotificationStrategy~
        +for_channels(channels) NotificationService
        +send(message) None
    }

    INotificationStrategy <|.. EmailStrategy
    INotificationStrategy <|.. SlackStrategy
    INotificationStrategy <|.. SMSStrategy
    NotificationStrategyFactory ..> INotificationStrategy : creates
    NotificationService --> INotificationStrategy : uses

    %% ─── INTERVIEWS ──────────────────────────────────────────────────────────
    class IInterviewRepository {
        <<interface>>
        +get_by_id(id) InterviewDTO
        +list(filters) Iterable~InterviewDTO~
        +add(data) InterviewDTO
        +evaluate(id, data) InterviewDTO
        +delete(id) None
    }

    class InterviewRepository {
        +get_by_id(id) InterviewDTO
        +list(filters) Iterable~InterviewDTO~
        +add(data) InterviewDTO
        +evaluate(id, data) InterviewDTO
        +delete(id) None
    }

    class InterviewService {
        -_repo: IInterviewRepository
        +schedule(data) InterviewDTO
        +get(id) InterviewDTO
        +list(filters) Iterable~InterviewDTO~
        +evaluate(id, data) InterviewDTO
        +delete(id) None
    }

    IInterviewRepository <|.. InterviewRepository
    InterviewService --> IInterviewRepository

    %% ─── ANALYTICS ───────────────────────────────────────────────────────────
    class AnalyticsService {
        +FUNNEL_ORDER: tuple
        +candidates_by_status() dict~str,int~
        +funnel() list~dict~
        +time_to_hire_seconds() dict
        +stale_candidates(days) int
    }

    %% ─── OBSERVER (Signal) ───────────────────────────────────────────────────
    class CandidateStatusChangedSignal {
        <<signal>>
        +send(candidate_id, email, name, from_status, to_status)
    }

    class StatusChangeNotificationHandler {
        <<receiver>>
        +handle(signal, **kwargs) None
    }

    CandidateService ..> CandidateStatusChangedSignal : fires
    CandidateStatusChangedSignal ..> StatusChangeNotificationHandler : notifies
    StatusChangeNotificationHandler ..> NotificationService : delegates
```

---

## Dependency Injection Flow

```
DRF View
  │
  ├─ get_candidate_service()        ← factory.py
  │      └─ CandidateService(repo=CandidateRepository())
  │                                         │
  │                              ICandidateRepository
  │                                         │
  │                              CandidateRepository  ← Django ORM
  │
  └─ Test: CandidateService(repo=InMemoryCandidateRepo())
                                     InMemoryCandidateRepo  ← dict
```
