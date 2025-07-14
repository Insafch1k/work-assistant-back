from project.utils.logger import Logger
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from datetime import datetime, time

from project.BL.job_bl import time_calculate
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
    try:
        current_user_tg = get_jwt_identity()
        curr_id = JobDAL.get_employer_id_by_tg(current_user_tg)
        if not curr_id:
            return jsonify({"error": "Только работодатели могут создавать объявления"}), 403

        data = request.get_json()
        fields = ["title", "wanted_job", "description", "salary", "date", "time_start", "time_end", "address",
                  "xp", "age", "car"]
        if any(field not in data or data[field] is None for field in fields):
            return jsonify({"error": "Неправильно заполнены поля"}), 400

        valid_xp = ["нет опыта", "от 1 года", "от 3 лет"]
        valid_age = ["старше 14 лет", "старше 16 лет", "старше 18 лет"]

        if data["xp"] not in valid_xp:
            return jsonify({"error": "Недопустимое значение для опыта работы. "
                                     "Допустимые значения: нет опыта, от 1 года, от 3 лет"}), 400
        if data["age"] not in valid_age:
            return jsonify({"error": "Недопустимое значение для возраста. "
                                     "Допустимые значения: старше 14 лет, старше 16 лет, старше 18 лет"}), 400
        if not isinstance(data["car"], bool):
            return jsonify({"error": "Поле car должно быть булевым (true/false)"}), 400

        new_job = JobDAL.add_job(curr_id, data["title"], data["wanted_job"], data["description"],
                                 data["salary"], data["date"], data["time_start"], data["time_end"], data["address"],
                                 data["is_urgent"], data["xp"], data["age"], data["car"])

        return jsonify({
            "job_id": new_job[0],
            "title": new_job[1],
            "wanted_job": new_job[2],
            "salary": new_job[3],
            "time_start": new_job[4],
            "time_end": new_job[5],
            "created_at": new_job[6].isoformat(),
            "address": new_job[7],
            "car": new_job[8],
            "message": "Объявление успешно создано"
        }), 200
    except Exception as e:
        Logger.error(f"Error create job {str(e)}")
        return jsonify({
            "message": f"Error create job {str(e)}"
        }), 500

@filter_router.route("/jobs/filter", methods=["POST"])
@jwt_required()
def filter_jobs():
    """Фильтрация вакансий"""
    try:
        current_user_tg = get_jwt_identity()

        data = request.get_json()
        temp_json = {"wanted_job": None, "address": None, "time_start": None, "time_end": None, "date": None,
                     "salary": None, "salary_to": None, "xp": None, "age": None, "car": None}

        valid_xp = ["нет опыта", "от 1 года", "от 3 лет"]
        valid_age = ["старше 14 лет", "старше 16 лет", "старше 18 лет"]

        if "xp" in data and data["xp"] is not None:
            if data["xp"] not in valid_xp:
                return jsonify({"error": "Недопустимое значение для опыта работы. "
                                         "Допустимые значения: нет опыта, от 1 года, от 3 лет"}), 400

        if "age" in data and data["age"]:
            if data["age"] not in valid_age:
                return jsonify({"error": "Недопустимое значение для возраста. "
                                         "Допустимые значения: старше 14 лет, старше 16 лет, старше 18 лет"}), 400

        if "car" in data and data["car"] is not None:
            if not isinstance(data["car"], bool):
                return jsonify({"error": "Поле car должно быть булевым (true/false)"}), 400

        for field, value in temp_json.items():
            if field in data:
                temp_json[field] = data[field]

        if temp_json["date"]:
            try:
                temp_json["date"] = f"{temp_json['date']} 00:00:00"
            except ValueError:
                return jsonify({"error": "Неверный формат даты. Используйте YYYY-MM-DD"}), 400

        if all((value is None) for value in temp_json.values()):
            return jsonify({"error": "Хотя бы одно поле должно быть заполнено или поля не корректны"}), 400

        is_urgent = False if (data["is_urgent"] is None) else data["is_urgent"]

        jobs = FilterDAL.get_filtered_jobs(wanted_job=temp_json["wanted_job"], address=temp_json["address"],
                                           time_start=temp_json["time_start"], time_end=temp_json["time_end"],
                                           date=temp_json["date"], salary=temp_json["salary"], salary_to=temp_json["salary_to"],
                                           is_urgent=is_urgent, xp=temp_json["xp"], age=temp_json["age"], car=temp_json["car"])

        if not jobs or not jobs[0]:
            return jsonify({"error": "Работа не найдена"}), 404

        jobs_json = []
        for job in jobs:
            hours = time_calculate(job[6], job[7])
            jobs_json.append({
                "job_id": job[0],
                "title": job[1],
                "wanted_job": job[2],
                "description": job[3],
                "salary": job[4],
                "date": job[5].isoformat() if job[5] else None,
                "time_hours": hours,
                "address": job[8],
                "is_urgent": job[9],
                "organization_name": job[10],
                "created_at": job[11].isoformat(),
                "rating": job[12],
                "photo": job[13],
                "xp": job[14],
                "age": job[15],
                "car": job[16]
            })
        return jsonify(jobs_json), 200
    except Exception as e:
        Logger.error(f"Error filter jobs {str(e)}")
        return jsonify({
            "message": f"Error filter jobs {str(e)}"
        }), 500

@history_router.route("/jobs/<int:job_id>/view", methods=["POST"])
@jwt_required()
def add_job_view(job_id):
    """Добавление связи для истории просмотра вакансий"""
    try:
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
    except Exception as e:
        Logger.error(f"Error add job view {str(e)}")
        return jsonify({
            "message": f"Error add job view {str(e)}"
        }), 500

@history_router.route("/jobs/history", methods=["GET"])
@jwt_required()
def get_view_history():
    """Получение истории просмотра вакансий"""
    try:
        current_user_tg = get_jwt_identity()
        curr_id = HistoryDAL.get_finder_id_by_tg(current_user_tg)
        if not curr_id:
            return jsonify({"error": "Пользователь не найден"}), 404

        history = HistoryDAL.get_view_history(curr_id)
        history_list = []
        for job in history:
            if len(job) >= 9:
                hours = time_calculate(job[5], job[6])
            else:
                hours = None

            history_list.append({
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
                "rating": job[11],
                "car": job[12]
            })

        if not history_list:
            return jsonify({"message": "Нет просмотренных вакансий"}), 404
        return jsonify(history_list), 200
    except Exception as e:
        Logger.error(f"Error get view history {str(e)}")
        return jsonify({
            "message": f"Error get view history {str(e)}"
        }), 500

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
    job_json = {
        "title": job[0].strip() if isinstance(job[0], str) else job[0],
        "salary": job[1],
        "address": job[2].strip() if isinstance(job[2], str) else job[2],
        "date": job[3].isoformat() if isinstance(job[3], datetime) else job[3],
        "time_start": job[4].strftime("%H:%M") if isinstance(job[4], time) else job[4],
        "time_end": job[5].strftime("%H:%M") if isinstance(job[5], time) else job[5],
        "is_urgent": job[6],
        "xp": job[7],
        "age": job[8],
        "description": job[9],
        "car": job[10],
        "is_favorite": job[11],
        "hours": time_calculate(job[4], job[5]) if job[4] and job[5] else None
    }

    return jsonify(job_json), 200

@employer_jobs_router.route("/jobs/employers", methods=["GET"])
@jwt_required()
def get_jobs_for_employers():
    """Получение списка вакансий для работодателя"""
    try:
        current_user_tg = get_jwt_identity()
        curr_id = Emplyers_Jobs.get_employer_id_by_tg(current_user_tg)
        if not curr_id:
            return jsonify({"error": "Пользователь не найден или не существует"}), 404

        jobs = Emplyers_Jobs.get_all_jobs(curr_id)
        if not jobs:
            return jsonify({"error": "Вакансии не найдены"}), 404

        jobs_json = []
        for job in jobs:
            try:
                hours = time_calculate(job[5], job[6]) if len(job) > 6 and job[5] and job[6] else None
                
                job_data = {
                    "job_id": job[0],
                    "employer_id": job[1],
                    "title": job[2],
                    "salary": job[3],
                    "address": job[4],
                    "time_hours": hours,
                    "is_favorite": job[7] if len(job) > 7 else False,
                    "is_urgent": job[8] if len(job) > 8 else False,
                    "created_at": job[9].isoformat() if len(job) > 9 and job[9] else None,
                    "photo": job[10] if len(job) > 10 else None,
                    "rating": job[11] if len(job) > 11 else None,
                    "car": job[12] if len(job) > 12 else None
                }
                jobs_json.append(job_data)
            except IndexError as ie:
                Logger.error(f"Ошибка обработки вакансии: {str(ie)}")
                continue

        return jsonify(jobs_json), 200
    except Exception as e:
        Logger.error(f"Ошибка при получении вакансий для работодателя: {str(e)}")
        return jsonify({"message": f"Ошибка при получении вакансий для работодателя: {str(e)}"}), 500

@finder_jobs_router.route("/jobs/finders", methods=["GET"])
@jwt_required()
def get_jobs_for_finders():
    """Получение списка вакансий для соискателя"""
    try:
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
                hours = time_calculate(job[5], job[6])
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
                "rating": job[11],
                "car": job[12]
            })

        return jsonify(jobs_list), 200
    except Exception as e:
        Logger.error(f"Error get jobs for finders {str(e)}")
        return jsonify({
            "message": f"Error get jobs for finders {str(e)}"
        }), 500

@employer_jobs_router.route("/jobs/me", methods=["GET"])
@jwt_required()
def get_my_jobs():
    """Получение своего списка вакансий для работодателя"""
    try:
        current_user_tg = get_jwt_identity()
        curr_id = Emplyers_Jobs.get_employer_id_by_tg(current_user_tg)
        if not curr_id:
            return jsonify({"error": "Пользователь не найден или не существует"}), 404

        jobs = Emplyers_Jobs.get_my_employer_jobs(curr_id)
        if not jobs:
            return jsonify({"error": "Вакансии не найдены"}), 404

        jobs_list = []
        for job in jobs:
            try:
                hours = time_calculate(job[5], job[6]) if len(job) > 6 and job[5] and job[6] else None
                
                job_data = {
                    "job_id": job[0],
                    "employer_id": job[1],
                    "title": job[2],
                    "salary": job[3],
                    "address": job[4],
                    "time_hours": hours,
                    "is_urgent": job[7] if len(job) > 7 else False,
                    "created_at": job[8].isoformat() if len(job) > 8 and job[8] else None,
                    "wanted_job": job[9] if len(job) > 9 else None,
                    "time_start": job[5].strftime("%H:%M") if len(job) > 5 and isinstance(job[5], time) else None,
                    "time_end": job[6].strftime("%H:%M") if len(job) > 6 and isinstance(job[6], time) else None,
                    "date": job[10].strftime("%d.%m.%Y") if len(job) > 10 and job[10] else None,
                    "xp": job[11] if len(job) > 11 else None,
                    "age": job[12] if len(job) > 12 else None,
                    "description": job[13] if len(job) > 13 else None,
                    "car": job[14] if len(job) > 14 else None
                }
                jobs_list.append(job_data)
            except IndexError as ie:
                Logger.error(f"Ошибка обработки вакансии: {str(ie)}")
                continue

        return jsonify(jobs_list), 200
    except Exception as e:
        Logger.error(f"Ошибка при получении моих вакансий: {str(e)}")
        return jsonify({"message": f"Ошибка при получении моих вакансий: {str(e)}"}), 500


@employer_jobs_router.route('/jobs/me/<int:job_id>', methods=["PATCH"])
@jwt_required()
def update_my_job(job_id):
    """Редактирование объявления"""
    try:
        current_user_tg = get_jwt_identity()
        curr_id = Emplyers_Jobs.get_employer_id_by_tg(current_user_tg)
        if not curr_id:
            return jsonify({"error": "Пользователь не найден или не существует"}), 404

        data = request.get_json()

        temp_json = {"title": None, "wanted_job": None, "description": None, "salary": None, "date": None,
                     "time_start": None, "time_end": None, "address": None, "is_urgent": None,
                     "xp": None, "age": None, "status": None, "car": None}

        for temp in temp_json:
            if temp in data:
                temp_json[temp] = data[temp]

        is_urgent = False if (temp_json["is_urgent"] is None) else data["is_urgent"]
        job = Emplyers_Jobs.update_my_employer_job(job_id, title=temp_json["title"], wanted_job=temp_json["wanted_job"],
                                                   description=temp_json["description"], salary=temp_json["salary"], date=temp_json["date"],
                                                   time_start=temp_json["time_start"], time_end=temp_json["time_end"], address=temp_json["address"],
                                                   is_urgent=is_urgent, xp=temp_json["xp"], age=temp_json["age"], status=temp_json["status"], car=temp_json["car"])
        if job:
            return jsonify({"message": "Профиль обновлён"}), 200
        return jsonify({"error": "Профиль не получилось обновить"})
    except Exception as e:
        Logger.error(f"Error update my job {str(e)}")
        return jsonify({
            "message": f"Error update my job {str(e)}"
        }), 500