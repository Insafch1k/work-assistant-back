from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from project.application.routes.favorite.jobs_favorite_schemas import AddJobToFavoriteValidateSchema
from project.domain.favorite.favorite_bl import FavoriteJobBL
from project.domain.jobs.base_job_bl import BaseJobBl
from project.utils.data_state import DataFailedMessage

job_favorite_router = Blueprint("jobs_favorite_router", __name__)


@job_favorite_router.route("/jobs/favorite", methods=["POST"])
@jwt_required()
def add_job_to_favorite():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        validate_data_state = AddJobToFavoriteValidateSchema.from_request(data)
        if not validate_data_state:
            return validate_data_state.to_response()

        job_id = validate_data_state.data.job_id
        data_state = FavoriteJobBL.add_job_to_favorite(user_id, job_id)

        return data_state.to_response()
    except Exception as e:
        return DataFailedMessage(f"Ошибка добавления вакансии в избранное", error=e).to_response()


@job_favorite_router.route("/jobs/favorite", methods=["GET"])
@jwt_required()
def get_list_of_favorites():
    try:
        user_id = get_jwt_identity()

        jobs_state = FavoriteJobBL.get_list_of_favorites(user_id)

        return jobs_state.to_response()
    except Exception as e:
        return DataFailedMessage(f"Ошибка вывода списка избранных", error=e).to_response()
