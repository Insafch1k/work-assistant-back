from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ValidationError, ConfigDict, field_validator

from project.application.entities.event import MetricEvents, PeriodType, MetricName
from project.utils.data_state import DataState, DataSuccess, DataFailedMessage


class TrackEventValidateSchema(BaseModel):
    event_name: MetricEvents
    user_id: int

    @field_validator('event_name', mode='before')
    def validate_name(cls, v):
        try:
            return MetricEvents(v)
        except Exception:
            raise ValueError(f"Такого события нету! Существующие события: {[e.value for e in MetricEvents]}")

    @classmethod
    def from_request(cls, json_data) -> DataState[TrackEventValidateSchema]:
        try:
            return DataSuccess(TrackEventValidateSchema(**json_data))
        except ValidationError as e:
            errors = [
                {"field": err["loc"][0],
                 "message": err["msg"]}
                for err in e.errors()
            ]
            return DataFailedMessage(f'Ошибка валидации при добавлении события: {errors}', error=e)

class GetMetricsValidateSchema(BaseModel):
    limit: int = 30
    period: PeriodType = PeriodType.DAY
    metric_name: MetricName

    @field_validator('period', mode='before')
    def validate_period(cls, v):
        try:
            return PeriodType(v)
        except Exception:
            raise ValueError(f"Неверный период! Возможные варианты: {[e.value for e in PeriodType]}")

    @field_validator('metric_name', mode='before')
    def validate_metric_name(cls, v):
        try:
            return MetricName(v)
        except Exception:
            raise ValueError(f"Такой метрики нету! Существующие метрики: {[e.value for e in MetricName]}")


    @classmethod
    def from_request(cls, json_data) -> DataState[GetMetricsValidateSchema]:
        try:
            return DataSuccess(GetMetricsValidateSchema(**json_data))
        except ValidationError as e:
            errors = [
                {"field": err["loc"][0],
                 "message": err["msg"]}
                for err in e.errors()
            ]
            return DataFailedMessage(f'Ошибка валидации при получении метрик: {errors}', error=e)