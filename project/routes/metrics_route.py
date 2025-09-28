from flask import Blueprint, request, jsonify

from project.BL.metrics_bl import MetricsBL
from project.DAL.profile_dal import ProfileDAL
from project.utils.is_admin import admin_required

metrics_router = Blueprint("metrics_router", __name__)

@metrics_router.route('/metrics/track_event', methods=['POST'])
def track_event():
    """
    Эндпоинт для трекинга событий
    Пример тела запроса:
    {
        "event_name": "vacancy_sent",
        "tg_id": "512523",
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        event_name = data.get('event_name')
        if not event_name:
            return jsonify({"error": "event_name is required"}), 400
        user_id = ProfileDAL.get_user_id_by_tg(data.get('tg_id'))
        MetricsBL.track_metric(event_name,user_id)

        return jsonify({
            "status": "success",
            "message": f"Event '{event_name}' tracked successfully"
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@metrics_router.route('/metrics/<metric_name>', methods=['GET'])
@admin_required()
def get_metrics(metric_name: str):
    """
    Получение метрик с различной гранулярностью
    Типы метрик: 'registered_users' - зарегестрированные,
    'active_users' - уникальные пользователи,
    'new_vacancies' - новые вакансии,
    'responses_count' - отклики на вакансии,
    'response_rate' - отношение откл/уникальный пользователей

    Параметры:
    ?period=day (hour, day, month, year)
    ?limit=30 (количество периодов)
    """
    try:
        period_type = request.args.get('period', 'day')
        limit = int(request.args.get('limit', '30'))

        if period_type not in ['hour', 'day', 'month']:
            return jsonify({
                "error": "period must be 'hour', 'day' or 'month'"
            }), 400

        metrics_data = MetricsBL.get_metrics_by_period(
            period_type=period_type,
            metric_name=metric_name,
            limit=limit
        )

        return jsonify({
            "metric": metric_name,
            "period": period_type,
            "data": metrics_data,
            "total_periods": len(metrics_data)
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500