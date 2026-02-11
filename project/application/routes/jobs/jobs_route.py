from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from project.application.entities.event import MetricEvents
from project.application.routes.jobs.jobs_schemas import CreateNewJobValidateSchema, UpdateJobSchema, \
    GetJobsValidateSchema
from project.application.routes.metrics.metric_schemas import TrackEventValidateSchema
from project.domain.jobs.base_job_bl import BaseJobBl
from project.domain.metrics.metric_bl import MetricsBL
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
        if data_state:
            MetricsBL.track_metric(TrackEventValidateSchema(event_name=MetricEvents.VacancyPublished,user_id=user_id))

        return data_state.to_response()
    except Exception as e:
        return DataFailedMessage(f"Ошибка добавления вакансии", error=e).to_response()

@job_router.route("/jobs/me", methods=["GET"])
@jwt_required()
def get_my_jobs():
    """вакансии текущего работодателя для стр мои объявления (id, title, time_end, time_start, salary, is_urgent, car, address)"""
    try:
        user_id = get_jwt_identity()
        data_state = BaseJobBl.get_my_jobs(user_id)

        return data_state.to_response()
    except Exception as e:
        return DataFailedMessage(f"Ошибка просмотра моих вакансии", error=e).to_response()

@job_router.route("/jobs", methods=["GET"])
@jwt_required()
def get_all_jobs():
    """Получение всех вакансий"""
    try:
        user_id = get_jwt_identity()

        validate_data_state = GetJobsValidateSchema.from_request(request.args)

        if not validate_data_state:
            return validate_data_state.to_response()

        data_state = BaseJobBl.get_all_jobs(user_id, validate_data_state.data)

        return data_state.to_response()
    except Exception as e:
        return DataFailedMessage(f"Ошибка вывода всех вакансий", error=e).to_response()

@job_router.route("/jobs/cities", methods=["GET"])
@jwt_required()
def get_cities():
    """Получение всех вакансий"""
    try:
        data_state = BaseJobBl.get_cities()

        return data_state.to_response()
    except Exception as e:
        return DataFailedMessage(f"Ошибка вывода населенных пунктов", error=e).to_response()

@job_router.route("/jobs/<int:job_id>", methods=["GET"])
@jwt_required()
def get_all_info_job(job_id: int):
    """Подробная информация вакансии"""
    try:
        user_id = get_jwt_identity()
        data_state = BaseJobBl.get_all_info_job(user_id, job_id)
        return data_state.to_response()

    except Exception as e:
        return DataFailedMessage(f"Ошибка просмотра вакансии", error=e).to_response()

@job_router.route("/jobs/<int:job_id>", methods=["PATCH"])
@jwt_required()
def update_job(job_id):
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        validate_data_state = UpdateJobSchema.from_request(data)

        if not validate_data_state:
            return validate_data_state.to_response()

        updated_data = validate_data_state.data.get_update_fields()
        data_state = BaseJobBl.update_job(job_id,user_id, updated_data)

        return data_state.to_response()

    except Exception as e:
        return DataFailedMessage(f"Ошибка обновления вакансии", error=e).to_response()

@job_router.route("/jobs/<int:job_id>", methods=["DELETE"])
@jwt_required()
def delete_job(job_id):
    try:
        user_id = get_jwt_identity()
        data_state = BaseJobBl.delete_job(job_id,user_id)

        return data_state.to_response()

    except Exception as e:
        return DataFailedMessage(f"Ошибка обновления вакансии", error=e).to_response()

