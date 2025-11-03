from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from project.application.routes.favorite.jobs_favorite_schemas import JobIdValidateSchema
from project.domain.favorite.favorite_bl import FavoriteJobBL
from project.domain.history.history_bl import HistoryBl
from project.domain.jobs.base_job_bl import BaseJobBl
from project.utils.data_state import DataFailedMessage

job_history_router = Blueprint("jobs_history_router", __name__)

@job_history_router.route("/jobs/history", methods=["GET"])
@jwt_required()
def get_list_of_jobs_history():
    try:
        user_id = get_jwt_identity()
        jobs_state = HistoryBl.get_list_of_jobs_history(user_id)

        return jobs_state.to_response()

    except Exception as e:
        return DataFailedMessage(f"Ошибка вывода списка истории просмотра вакансий", error=e).to_response()

@job_history_router.route("/jobs/history", methods=["POST"])
@jwt_required()
def add_job_to_history():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        validate_data_state = JobIdValidateSchema.from_request(data)
        if not validate_data_state:
            return validate_data_state.to_response()

        job_id = validate_data_state.data.job_id
        data_state = HistoryBl.add_job_to_history(user_id, job_id)

        return data_state.to_response()
    except Exception as e:
        return DataFailedMessage(f"Ошибка добавления вакансии в историю", error=e).to_response()