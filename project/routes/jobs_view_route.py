from flask import jsonify, Blueprint
from flask_jwt_extended import get_jwt_identity, jwt_required
from project.DAL.jobs_view_for_employer_dal import Emplyers_Jobs
from project.DAL.jobs_view_for_finder_dal import Finder_Jobs
from datetime import datetime

employer_jobs = Blueprint("employer_jobs_router", __name__)
finder_jobs = Blueprint("finder_jobs_router", __name__)

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

@finder_jobs.route("/jobs/finders", methods=["GET"])
@jwt_required()
def get_jobs_for_finders():
    current_user_tg = get_jwt_identity()
    curr_id = Finder_Jobs.get_finder_id_by_tg(current_user_tg)
    if not curr_id:
        return jsonify({"error": "Пользователь не найден или не существует"}), 404
    
    jobs = Finder_Jobs.get_all_jobs(curr_id)
    jobs_list = []
    for job in jobs:
        if len(job) >= 5:
            try:
                if isinstance(job[4], datetime) and isinstance(job[5], datetime):
                    time_diff = job[5] - job[4]
                elif isinstance(job[4], str) and isinstance(job[5], str):
                    time_diff = datetime.strptime(job[5], "%a, %d %b %Y %H:%M:%S %Z") - \
                               datetime.strptime(job[4], "%a, %d %b %Y %H:%M:%S %Z")
                else:
                    time_diff = None
                
                hours = round(time_diff.total_seconds() / 3600, 2) if time_diff else None
            except (ValueError, TypeError, AttributeError) as e:
                print(f"Ошибка обработки времени: {e}")
                hours = None
        else:
            hours = None

        jobs_list.append({
            "job_id" : job[0],
            "title": job[1],
            "salary": job[2],
            "address": job[3],
            "time_hours": hours
        })
    
    return jsonify(jobs_list), 200
