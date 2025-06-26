from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from project.DAL.filter_dal import FilterDAL

filter_router = Blueprint("filter_router", __name__)


@filter_router.route('/jobs/filter', methods=['GET'])
@jwt_required()
def filter_jobs():
    current_user_tg = get_jwt_identity()
    curr_id = FilterDAL.get_finder_id_by_tg(current_user_tg)
    if not curr_id:
        return jsonify({"error": "Пользователь не найден"}), 404

    data = request.get_json()
    jobs = FilterDAL.get_filtered_jobs(
        wanted_job=data["wanted_job"],
        address=data["address"],
        time_start=data["time_start"],
        time_end=data["time_end"],
        date=data["date"],
        salary=data["salary"],
        is_urgent=data["is_urgent"],
        xp=data["xp"],
        age=data["age"]
    )

    return jsonify([{
        "title": job[0],
        "salary": job[1],
        "time_delta": str(job[2]) if job[2] else None,
        "address": job[3],
        "organization_name": job[4]
    } for job in jobs]), 200