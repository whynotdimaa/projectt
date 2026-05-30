# Domain Model — HR Candidate Evaluation System

## Модель предметної області

```mermaid
classDiagram
    class Candidate {
        +int id
        +str first_name
        +str last_name
        +str email  <<unique>>
        +str phone
        +str resume_url
        +str desired_position
        +CandidateStatus status
        +datetime created_at
        +datetime updated_at
    }

    class CandidateStatus {
        <<enumeration>>
        NEW
        SCREENING
        INTERVIEW
        OFFER
        HIRED
        REJECTED
    }

    class StatusHistory {
        +int id
        +str from_status
        +str to_status
        +datetime changed_at
    }

    class User {
        +int id
        +str email  <<unique>>
        +str first_name
        +str last_name
        +str phone
        +UserRole role
    }

    class UserRole {
        <<enumeration>>
        RECRUITER
        INTERVIEWER
        ADMIN
    }

    class Vacancy {
        +int id
        +str title
        +str department
        +str description
        +bool is_open
        +datetime created_at
        +datetime closed_at
    }

    class Interview {
        +int id
        +datetime scheduled_at
        +int score   [1..10, nullable]
        +str comment
        +datetime created_at
        +datetime evaluated_at [nullable]
    }

    Candidate "1" --> "1" CandidateStatus : has status
    Candidate "1" --> "0..*" StatusHistory : has history
    StatusHistory "0..*" --> "0..1" User : changed_by

    User "1" --> "1" UserRole : has role
    User "1" --> "0..*" Vacancy : recruits for
    User "1" --> "0..*" Interview : recruiter
    User "1" --> "0..*" Interview : interviewer

    Interview "0..*" --> "1" Candidate : evaluates
    Interview "0..*" --> "1" Vacancy : related_to [optional]
```

---

## Стейт-машина кандидата

```mermaid
stateDiagram-v2
    [*] --> NEW : create()

    NEW --> SCREENING : move_to_screening()
    NEW --> REJECTED : reject()

    SCREENING --> INTERVIEW : schedule_interview()
    SCREENING --> REJECTED : reject()

    INTERVIEW --> OFFER : make_offer()
    INTERVIEW --> REJECTED : reject()

    OFFER --> HIRED : hire()
    OFFER --> REJECTED : reject()

    HIRED --> [*]
    REJECTED --> [*]
```

### Дозволені переходи (ALLOWED_TRANSITIONS)

| Від | До |
|-----|----|
| `NEW` | `SCREENING`, `REJECTED` |
| `SCREENING` | `INTERVIEW`, `REJECTED` |
| `INTERVIEW` | `OFFER`, `REJECTED` |
| `OFFER` | `HIRED`, `REJECTED` |
| `HIRED` | — (термінальний) |
| `REJECTED` | — (термінальний) |

---

## Бізнес-правила

1. **Унікальний email** — конфлікт при спробі створити дублікат
2. **Суворі переходи статусів** — тільки по дозволених ребрах графу
3. **Аудит** — кожна зміна статусу записується в `StatusHistory`
4. **Нотифікація** — при кожній зміні статусу Celery відправляє повідомлення
5. **RBAC** — Recruiter/Admin: повний доступ; Interviewer: читання + оцінка
6. **Score** — оцінка 1-10, виставляється лише Interviewer
7. **Термінальні статуси** — HIRED і REJECTED незмінні
