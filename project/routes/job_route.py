from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from project.DAL.job_dal import JobDAL

job_router = Blueprint("job_router", __name__)


@job_router.route('/jobs', methods=['POST'])
@jwt_required()
def create_job():
    """Создание новой вакансии"""
    current_user_tg = get_jwt_identity()
    employer = JobDAL.get_finder_id_by_tg(current_user_tg)
    if not employer:
        return jsonify({"error": "Только работодатели могут создавать объявления"}), 403

    data = request.get_json()
    new_job = JobDAL.add_job(data["employer_id"], data["title"], data["wanted_job"], data["description"], data["salary"],
                             data["date"], data["time_start"], data["time_end"], data["address"], data["is_urgent"],
                             data["xp"], data["age"])

    return jsonify({
        "job_id": new_job[0],
        "title": new_job[1],
        "wanted_job": new_job[2],
        "salary": new_job[2],
        "time_delta": str(new_job[2]) if new_job[2] else None,
        "created_at": new_job[3].isoformat(),
        "address": new_job[3],
        "organization_name": new_job[4]
    }), 200