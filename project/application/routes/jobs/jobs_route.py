from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from project.application.routes.jobs.jobs_schemas import CreateNewJobValidateSchema
from project.domain.jobs.base_job_bl import BaseJobBl
from project.utils.data_state import DataFailedMessage

job_router = Blueprint("jobs_router", __name__)


@job_router.route("/jobs", methods=["POST"])
@jwt_required()
def create_job():
    """Создание новой работы"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        validate_data_state = CreateNewJobValidateSchema.from_request(data)

        if not validate_data_state:
            return validate_data_state.to_response()

        result = validate_data_state.data
        data_state = BaseJobBl.add_job(user_id, result)

        return data_state.to_response()
    except Exception as e:
        return DataFailedMessage(f"Ошибка добавления вакансии", error=e).to_response()
