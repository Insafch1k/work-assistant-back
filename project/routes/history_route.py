from flask import jsonify, Blueprint
from flask_jwt_extended import get_jwt_identity, jwt_required
from project.DAL.history_dal import HistoryDAL

history_router = Blueprint("history_router", __name__)

@history_router.route("/jobs/<int:job_id>/view", methods=["POST"])
@jwt_required()
def add_job_view(job_id):
    current_user_tg = get_jwt_identity()
    curr_id = HistoryDAL.get_finder_id_by_tg(current_user_tg)
    if not curr_id:
        return jsonify({"error": "Пользователь не найден"}), 404
    
    result = HistoryDAL.add_job_view(curr_id, job_id)
    if not result:
        return jsonify({"error": "Просмотр уже существует или не удалось добавить"}), 400
    
    return jsonify({
        "history_id": result[0],
        "finder_id" : result[1],
        "job_id" : result[2],
        "viewed_at" : result[3].isoformat() if result[3] else None
    }), 200

@history_router.route("/jobs/history", methods=["GET"])
@jwt_required()
def get_view_history():
    current_user_tg = get_jwt_identity()
    curr_id = HistoryDAL.get_finder_id_by_tg(current_user_tg)
    if not curr_id:
        return jsonify({"error" : "Пользователь не найден"}), 404
    
    history = HistoryDAL.get_view_history(curr_id)
    history_list = []
    for job in history:
        history_list.append({
            "job_id" : job[0],
            "title" : job[1],
            "salary" : job[2],
            "address" : job[3],
            "time_start" : job[4].isoformat() if job[4] else None,
            "time_end" : job[5].isoformat() if job[5] else None
        })
    
    return jsonify(history_list), 200
    