from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from project.application.routes.jobs.jobs_schemas import CreateNewJobValidateSchema, UpdateJobSchema
from project.domain.jobs.base_job_bl import BaseJobBl
from project.utils.data_state import DataFailedMessage

from loguru import logger

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


@job_router.route("/jobs", methods=["GET"])
@jwt_required()
def get_all_jobs():
    """Получение всех вакансий"""
    try:
        user_id = get_jwt_identity()
        data_state = BaseJobBl.get_all_jobs(user_id)
        if not data_state:
            return data_state.to_response()

        return jsonify(data_state), 200
    except Exception as e:
        return DataFailedMessage(f"Ошибка вывода всех вакансий", error=e).to_response()


@job_router.route("/jobs/<int:job_id>/see_all", methods=["GET"])
@jwt_required()
def get_all_info_job(job_id: int):
    """Подробная информация вакансии"""
    try:
        user_id = get_jwt_identity()
        data_state = BaseJobBl.get_all_info_job(user_id, job_id)
        if not data_state:
            return data_state.to_response()

        return jsonify(data_state), 200
    except Exception as e:
        return DataFailedMessage(f"Ошибка просмотра вакансии", error=e).to_response()

@job_router.route("/jobs/<int:job_id>/update", methods=["PATCH"])
@jwt_required()
def update_job(job_id):
    try:
        data = request.get_json()
        logger.info(f"Data from request {data}")
        validate_data_state = UpdateJobSchema.from_request(data)
        logger.info(f"Data after validate {validate_data_state.data}")

        if not validate_data_state:
            return validate_data_state.to_response()

        updated_data = validate_data_state.data.get_update_fields()
        logger.info(f"data after update {updated_data}")
        data_state = BaseJobBl.update_job(job_id, updated_data)

        return data_state.to_response()

    except Exception as e:
        return DataFailedMessage(f"Ошибка обновления вакансии", error=e).to_response()

