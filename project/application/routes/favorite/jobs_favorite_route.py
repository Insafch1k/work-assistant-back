from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from project.application.routes.favorite.jobs_favorite_schemas import AddJobToFavoriteValidateSchema
from project.domain.jobs.base_job_bl import BaseJobBl
from project.utils.data_state import DataFailedMessage

job_favorite_router = Blueprint("jobs_favorite_router", __name__)


@job_favorite_router.route("/jobs/favorite", methods=["POST"])
@jwt_required()
def add_job_to_favorite(job_id):
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        validate_data_state = AddJobToFavoriteValidateSchema.from_request(data)
        if not validate_data_state:
            return validate_data_state.to_response()

        result = validate_data_state.data
        data_state = BaseJobBl.add_job(user_id, result)

        return data_state.to_response()
    except Exception as e:
        return DataFailedMessage(f"Ошибка добавления вакансии в избранное", error=e).to_response()