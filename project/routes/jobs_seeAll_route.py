from flask import jsonify, Blueprint
from flask_jwt_extended import get_jwt_identity, jwt_required
from project.DAL.jobs_seeAll_dal import Jobs
from datetime import datetime

jobs_seeAll = Blueprint("jobs_see_All_route", __name__)

@jobs_seeAll.route("/jobs/<int:job_id>/seeall", methods=["GET"])
@jwt_required()
def get_job_seeAll_finders(job_id):
    # Проверка авторизации пользователя
    current_user_tg = get_jwt_identity()
    curr_id = Jobs.get_finder_id_by_tg(current_user_tg)
    if not curr_id:
        return jsonify({"error": "Пользователь не найден или не существует"}), 404
    
    # Получение данных о работе
    job_data = Jobs.get_job_seeAll(job_id)
    if not job_data or not job_data[0]:
        return jsonify({"error": "Работа не найдена"}), 404
    
    job = job_data[0]  # Получаем первую (и единственную) запись
    
    # Вычисление продолжительности работы
    hours = None  # Инициализируем переменную
    
    try:
        if isinstance(job[3], datetime) and isinstance(job[4], datetime):
            time_diff = job[4] - job[3]
            hours = round(time_diff.total_seconds() / 3600, 2)
        elif isinstance(job[3], str) and isinstance(job[4], str):
            time_diff = datetime.strptime(job[4], "%a, %d %b %Y %H:%M:%S %Z") - \
                       datetime.strptime(job[3], "%a, %d %b %Y %H:%M:%S %Z")
            hours = round(time_diff.total_seconds() / 3600, 2)
    except (ValueError, TypeError, AttributeError) as e:
        print(f"Ошибка обработки времени: {e}")

    # Формирование ответа
    job_json = {
        "title": job[0].strip() if isinstance(job[0], str) else job[0],
        "salary": job[1],
        "address": job[2].strip() if isinstance(job[2], str) else job[2],
        "date": job[3].isoformat() if isinstance(job[3], datetime) else job[3],
        "hours": hours,
        "is_urgent": job[5],
        "work_xp": job[6],
        "age_restrict": job[7]
    }

    return jsonify(job_json), 200