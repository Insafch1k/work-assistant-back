from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from datetime import datetime, time

from project.DAL.job_dal import JobDAL
from project.DAL.filter_dal import FilterDAL
from project.DAL.history_dal import HistoryDAL
from project.DAL.jobs_seeAll_dal import Jobs
from project.DAL.jobs_view_for_employer_dal import Emplyers_Jobs
from project.DAL.jobs_view_for_finder_dal import Finder_Jobs

job_router = Blueprint("job_router", __name__)
filter_router = Blueprint("filter_router", __name__)
history_router = Blueprint("history_router", __name__)
jobs_see_All_route = Blueprint("jobs_see_All_route", __name__)
employer_jobs_router = Blueprint("employer_jobs_router", __name__)
finder_jobs_router = Blueprint("finder_jobs_router", __name__)


@job_router.route("/jobs", methods=["POST"])
@jwt_required()
def create_job():
    """Создание новой вакансии"""
    current_user_tg = get_jwt_identity()
    curr_id = JobDAL.get_employer_id_by_tg(current_user_tg)
    if not curr_id:
        return jsonify({"error": "Только работодатели могут создавать объявления"}), 403

    data = request.get_json()
    fields = ["title", "wanted_job", "description", "salary", "date", "time_start", "time_end", "address",
              "is_urgent", "xp", "age"]
    if any(field not in data or not data[field] for field in fields):
        return jsonify({"error": "Неправильно заполнены поля"}), 400

    valid_xp = ["нет опыта", "от 1 года", "от 3 лет"]
    valid_age = ["старше 14 лет", "старше 16 лет", "старше 18 лет"]

    if data["xp"] not in valid_xp:
        return jsonify({"error": "Недопустимое значение для опыта работы. "
                                 "Допустимые значения: нет опыта, от 1 года, от 3 лет"}), 400

    if data["age"] not in valid_age:
        return jsonify({"error": "Недопустимое значение для возраста. "
                                 "Допустимые значения: старше 14 лет, старше 16 лет, старше 18 лет"}), 400

    new_job = JobDAL.add_job(curr_id, data["title"], data["wanted_job"], data["description"],
                             data["salary"], data["date"], data["time_start"], data["time_end"], data["address"],
                             data["is_urgent"], data["xp"], data["age"])

    print({
        "job_id": new_job[0],
        "title": new_job[1],
        "wanted_job": new_job[2],
        "salary": new_job[3],
        "time_start": new_job[4],
        "time_end": new_job[5],
        "created_at": new_job[6].isoformat(),
        "address": new_job[7]
    })
    return jsonify({"message": "Объявление успешно создано"}), 200


@filter_router.route("/jobs/filter", methods=["GET"])
@jwt_required()
def filter_jobs():
    """Фильтрация вакансий"""
    current_user_tg = get_jwt_identity()
    curr_id = FilterDAL.get_finder_id_by_tg(current_user_tg)
    if not curr_id:
        return jsonify({"error": "Пользователь не найден"}), 404

    data = request.get_json()
    temp_json = {"wanted_job": None, "address": None, "time_start": None, "time_end": None, "date": None,
                 "salary": None, "is_urgent": None, "xp": None, "age": None}

    for temp in temp_json:
        if temp in data:
            temp_json[temp] = data[temp]

    if temp_json["date"]:
        try:
            temp_json["date"] = f"{temp_json['date']} 00:00:00"
        except ValueError:
            return jsonify({"error": "Неверный формат даты. Используйте YYYY-MM-DD"}), 400

    jobs = FilterDAL.get_filtered_jobs(wanted_job=temp_json["wanted_job"], address=temp_json["address"],
                                       time_start=temp_json["time_start"], time_end=temp_json["time_end"],
                                       date=temp_json["date"], salary=temp_json["salary"],
                                       is_urgent=temp_json["is_urgent"],
                                       xp=temp_json["xp"], age=temp_json["age"])

    if not jobs or not jobs[0]:
        return jsonify({"error": "Работа не найдена"}), 404

    jobs_json = []
    for job in jobs:
        hours = None

        try:
            if isinstance(job[6], datetime) and isinstance(job[7], datetime):
                time_diff = job[7] - job[6]
                hours = round(time_diff.total_seconds() / 3600, 2)
            elif isinstance(job[6], str) and isinstance(job[7], str):
                time_diff = datetime.strptime(job[7], "%H:%M:%S") - datetime.strptime(job[6], "%H:%M:%S")
                hours = round(time_diff.total_seconds() / 3600, 2)
        except (ValueError, TypeError, AttributeError) as e:
            print(f"Ошибка обработки времени: {e}")

        jobs_json.append({
            "job_id": job[0],
            "title": job[1],
            "wanted_job": job[2],
            "description": job[3],
            "salary": job[4],
            "date": job[5].isoformat() if job[5] else None,
            "hours": hours,
            "address": job[8],
            "is_urgent": job[9],
            "organization_name": job[10],
            "created_at": job[11].isoformat()
        })

    return jsonify(jobs_json), 200


@history_router.route("/jobs/<int:job_id>/view", methods=["POST"])
@jwt_required()
def add_job_view(job_id):
    """Добавление связи для истории просмотра вакансий"""
    current_user_tg = get_jwt_identity()
    curr_id = HistoryDAL.get_finder_id_by_tg(current_user_tg)
    if not curr_id:
        return jsonify({"error": "Пользователь не найден"}), 404

    result = HistoryDAL.add_job_view(curr_id, job_id)
    if not result:
        return jsonify({"error": "Просмотр уже существует или не удалось добавить"}), 400

    return jsonify({
        "history_id": result[0],
        "finder_id": result[1],
        "job_id": result[2],
        "viewed_at": result[3].isoformat() if result[3] else None
    }), 200


@history_router.route("/jobs/history", methods=["GET"])
@jwt_required()
def get_view_history():
    """Получение истории просмотра вакансий"""
    current_user_tg = get_jwt_identity()
    curr_id = HistoryDAL.get_finder_id_by_tg(current_user_tg)
    if not curr_id:
        return jsonify({"error": "Пользователь не найден"}), 404

    history = HistoryDAL.get_view_history(curr_id)
    history_list = []
    for job in history:
        history_list.append({
            "job_id": job[0],
            "title": job[1],
            "salary": job[2],
            "address": job[3],
            "time_start": job[4].isoformat() if job[4] else None,
            "time_end": job[5].isoformat() if job[5] else None
        })

    return jsonify(history_list), 200


@jobs_see_All_route.route("/jobs/<int:job_id>/seeall", methods=["GET"])
@jwt_required()
def get_job_seeAll_finders(job_id):
    """Подробное описание объявления"""
    current_user_tg = get_jwt_identity()
    curr_id = Jobs.get_finder_id_by_tg(current_user_tg)
    if not curr_id:
        return jsonify({"error": "Пользователь не найден или не существует"}), 404

    job_data = Jobs.get_job_seeAll(curr_id, job_id)
    if not job_data:
        return jsonify({"error": "Работа не найдена"}), 404

    job = job_data[0]

    try:
        if isinstance(job[4], datetime) and isinstance(job[5], datetime):
            time_diff = job[5] - job[4]

        elif isinstance(job[4], str) and isinstance(job[5], str):
            t_start = datetime.strptime(job[4], "%H:%M:%S").time()
            t_end = datetime.strptime(job[5], "%H:%M:%S").time()

            dt_start = datetime.combine(datetime.today(), t_start)
            dt_end = datetime.combine(datetime.today(), t_end)

            time_diff = dt_end - dt_start

        elif isinstance(job[4], time) and isinstance(job[5], time):
            dt_start = datetime.combine(datetime.today(), job[4])
            dt_end = datetime.combine(datetime.today(), job[5])
            time_diff = dt_end - dt_start
        else:
            time_diff = None

        hours = round(time_diff.total_seconds() / 3600, 2) if time_diff else None
    except (ValueError, TypeError, AttributeError) as e:
        print(f"Ошибка обработки времени: {e}")
        hours = None

    job_json = {
        "title": job[0].strip() if isinstance(job[0], str) else job[0],
        "salary": job[1],
        "address": job[2].strip() if isinstance(job[2], str) else job[2],
        "date": job[3].isoformat() if isinstance(job[3], datetime) else job[3],
        "hours": hours,
        "is_urgent": job[6],
        "xp": job[7],
        "age": job[8],
        "description": job[9],
        "is_favorite": job[10]
    }

    return jsonify(job_json), 200


@employer_jobs_router.route("/jobs/employers", methods=["GET"])
@jwt_required()
def get_jobs_for_employers():
    """Получение списка вакансий для работодателя"""
    current_user_tg = get_jwt_identity()
    curr_id = Emplyers_Jobs.get_employer_id_by_tg(current_user_tg)
    if not curr_id:
        return jsonify({"error": "Пользователь не найден или не существует"})

    jobs = Emplyers_Jobs.get_all_jobs(curr_id)
    jobs_json = []

    for job in jobs:
        if len(job) >= 9:
            #Добавить это в BL
            try:
                if isinstance(job[5], str) and isinstance(job[6], str):
                    t_start = datetime.strptime(job[5], "%H:%M:%S").time()
                    t_end = datetime.strptime(job[6], "%H:%M:%S").time()

                    dt_start = datetime.combine(datetime.today(), t_start)
                    dt_end = datetime.combine(datetime.today(), t_end)

                    time_diff = dt_end - dt_start

                elif isinstance(job[5], time) and isinstance(job[6], time):
                    dt_start = datetime.combine(datetime.today(), job[5])
                    dt_end = datetime.combine(datetime.today(), job[6])
                    time_diff = dt_end - dt_start

                elif isinstance(job[5], datetime) and isinstance(job[6], datetime):
                    time_diff = job[6] - job[5]
                else:
                    time_diff = None

                hours = round(time_diff.total_seconds() / 3600, 2) if time_diff else None
            except (ValueError, TypeError, AttributeError) as e:
                print(f"Ошибка обработки времени: {e}")
                hours = None
        else:
            hours = None

        jobs_json.append({
            "job_id": job[0],
            "employer_id": job[1],
            "title": job[2],
            "salary": job[3],
            "address": job[4],
            "time_hours": hours,
            "is_favorite": job[7],
            "is_urgent": job[8],
            "created_at": job[9].isoformat(),
            "photo": job[10],
            "rating": job[11]
        })

    return jsonify(jobs_json), 200


@finder_jobs_router.route("/jobs/finders", methods=["GET"])
@jwt_required()
def get_jobs_for_finders():
    """Получение списка вакансий для соискателя"""
    current_user_tg = get_jwt_identity()
    curr_id = Finder_Jobs.get_finder_id_by_tg(current_user_tg)
    if not curr_id:
        return jsonify({"error": "Пользователь не найден или не существует"}), 404

    jobs = Finder_Jobs.get_all_jobs(curr_id)
    if not jobs or not jobs[0]:
        return jsonify({"error": "Работа не найдена"}), 404

    jobs_list = []
    for job in jobs:
        if len(job) >= 6:
            try:
                if isinstance(job[5], datetime) and isinstance(job[6], datetime):
                    time_diff = job[6] - job[5]

                elif isinstance(job[5], str) and isinstance(job[6], str):
                    t_start = datetime.strptime(job[5], "%H:%M:%S").time()
                    t_end = datetime.strptime(job[6], "%H:%M:%S").time()

                    dt_start = datetime.combine(datetime.today(), t_start)
                    dt_end = datetime.combine(datetime.today(), t_end)

                    time_diff = dt_end - dt_start

                elif isinstance(job[5], time) and isinstance(job[6], time):
                    dt_start = datetime.combine(datetime.today(), job[5])
                    dt_end = datetime.combine(datetime.today(), job[6])
                    time_diff = dt_end - dt_start
                else:
                    time_diff = None

                hours = round(time_diff.total_seconds() / 3600, 2) if time_diff else None
            except (ValueError, TypeError, AttributeError) as e:
                print(f"Ошибка обработки времени: {e}")
                hours = None
        else:
            hours = None

        jobs_list.append({
            "job_id": job[0],
            "employer_id": job[1],
            "title": job[2],
            "salary": job[3],
            "address": job[4],
            "time_hours": hours,
            "is_favorite": job[7],
            "is_urgent": job[8],
            "created_at": job[9],
            "photo": job[10],
            "rating": job[11]
        })

    return jsonify(jobs_list), 200
