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

    jobs_json = []
    for job in jobs:
        jobs_json.append({
            "job_id": job[0],
            "title": job[1],
            "wanted_job": job[2],
            "description": job[3],
            "salary": job[4],
            "date": job[5].isoformat() if job[5] else None,
            "time_start": job[6].isoformat() if job[6] else None,
            "time_end": job[7].isoformat() if job[7] else None,
            "address": job[8],
            "is_urgent": job[9],
            "organization_name": job[10],
            "created_at": job[11].isoformat()
        })

    return jsonify(jobs_json), 200