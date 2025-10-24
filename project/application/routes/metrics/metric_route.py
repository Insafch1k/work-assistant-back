from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from project.application.routes.metrics.metric_schemas import GetMetricsValidateSchema, TrackEventValidateSchema
from project.domain.admin.admin_bl import AdminBl
from project.domain.metrics.metric_bl import MetricsBL
from project.utils.data_state import  DataFailedMessage
from project.utils.is_admin import admin_required

mertic_router = Blueprint("mertic_router", __name__)


@mertic_router.route('/metrics/track_event', methods=["POST"])
@jwt_required()
def track_event():
    """
    Эндпоинт для трекинга событий
    Пример тела запроса:
    {
        "event_name": "vacancy_sent",
        "user_id": "512523",
    }
    """
    try:
        json_data = request.get_json()
        validate_data_state = TrackEventValidateSchema.from_request(json_data)
        if not validate_data_state:
            return validate_data_state.to_response()

        result = validate_data_state.data
        metric_data_state = MetricsBL.track_metric(result)
        return metric_data_state.to_response()
    except Exception as e:
        return DataFailedMessage("Ошибка записи события", error=e).to_response()

@mertic_router.route('/metrics/get_metric/', methods=['POST'])
@admin_required()
def get_metrics():
    """
    Получение метрик с различной гранулярностью
    Типы метрик: 'registered_users' - зарегестрированные,
    'active_users' - уникальные пользователи,
    'new_vacancies' - новые вакансии,
    'responses_count' - отклики на вакансии,
    'response_rate' - отношение откл/уникальный пользователей

    Параметры:
    {period=day (hour, day, month, year)
    limit=30 (количество периодов)
    metric_name}
    """

    try:
        json_data = request.get_json()
        validate_data_state = GetMetricsValidateSchema.from_request(json_data)
        if not validate_data_state:
            return validate_data_state.to_response()

        result = validate_data_state.data
        metric_data_state = MetricsBL.get_metrics_by_period(result)
        return metric_data_state.to_response()

    except Exception as e:
        return DataFailedMessage("Ошибка получении метрик", error=e).to_response()


