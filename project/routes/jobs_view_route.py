from flask import jsonify, Blueprint
from flask_jwt_extended import get_jwt_identity, jwt_required
from project.DAL.jobs_view_for_employer_dal import Emplyers_Jobs

employer_jobs = Blueprint("employer_jobs_router", __name__)

@employer_jobs.route("/jobs/employers", methods=["GET"])
@jwt_required()
def get_jobs_for_employers():
    current_user_tg = get_jwt_identity()
    curr_id = Emplyers_Jobs.get_finder_id_by_tg(current_user_tg)
    if not curr_id:
        return jsonify({"error" : "Пользователь не найден или не существует"})
    
    jobs = Emplyers_Jobs.get_all_jobs(curr_id)
    jobs_list = []
    for job in jobs:
        jobs_list.append({
            "job_id" : job[0],
            "employer_id" : job[1],
            "title" : job[2],
            "salary" : job[3],
            "address" : job[4],
            "time_start" : job[5].isoformat() if job[5] else None,
            "time_end" : job[6].isoformat() if job[6] else None,
            "created_at" : job[7].isoformat()
        })
    
    return jsonify(jobs), 200
