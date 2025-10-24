from __future__ import annotations
from enum import Enum
from pydantic import BaseModel

class MetricEvents(Enum):
    UserRegistered = 'user_registered'
    VacancyPublished = 'vacancy_published'
    vacancySent = 'vacancy_sent'

class PeriodType(Enum):
    HOUR = 'hour'
    DAY = 'day'
    MONTH = 'month'
    YEAR = 'year'

class MetricName(Enum):
    REGISTERED_USERS = 'registered_users'
    ACTIVE_USERS = 'active_users'
    NEW_VACANCIES = 'new_vacancies'
    RESPONSES_COUNT = 'responses_count'
    RESPONSE_RATE = 'response_rate'
