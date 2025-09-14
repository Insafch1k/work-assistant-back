from project.BL.metrics_bl import MetricsBL
from project.utils.logger import Logger
from project.utils.metric_events import MetricEvents
from project.utils.photo_transform import photo_url_convert
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
        Logger.info(f"Received data: {data}")

        required_fields = ["title", "wanted_job", "description", "salary", "date", 
                         "time_start", "time_end", "address", "city", "xp", "age", "car"]
        if any(field not in data or data[field] is None for field in required_fields):
            return jsonify({"error": "Неправильно заполнены поля"}), 400

        try:
            if '.' in data['date']:
                day, month, year = data["date"].split('.')
                data["date"] = f"{year}-{month}-{day}"

            job_date = datetime.strptime(data["date"], "%Y-%m-%d").date()
            if job_date < datetime.now().date():
                return jsonify({"error": "Нельзя указывать прошедшую дату для вакансии"}), 400

            if job_date == datetime.now().date():
                current_time = datetime.now().time()
                if data["time_start"]:
                    start_time = datetime.strptime(data["time_start"], "%H:%M").time()
                    if start_time < current_time:
                        return jsonify({"error": "Нельзя указывать прошедшее время для вакансии на сегодня"}), 400
        except Exception as e:
            Logger.error(f"Error parsing date: {str(e)}")
            return jsonify({"error": "Неверный формат даты. Используйте DD.MM.YYYY или YYYY-MM-DD"}), 400

        new_job = JobDAL.add_job(
            curr_id, 
            data["title"], 
            data["wanted_job"], 
            data["description"],
            data["salary"], 
            data["date"], 
            data["time_start"], 
            data["time_end"], 
            data["address"],
            data["city"],  # Добавляем город
            data.get("is_urgent", False),
            data["xp"], 
            data["age"], 
            data.get("car", False)
        )

        if not new_job:
            return jsonify({"error": "Не удалось создать вакансию"}), 500
        MetricsBL.track_metric(MetricEvents.VacancyPublished,curr_id)
        response_data = {
            "job_id": new_job[0],
            "title": new_job[1],
            "wanted_job": new_job[2],
            "salary": new_job[3],
            "time_start": str(new_job[4]) if new_job[4] else None,
            "time_end": str(new_job[5]) if new_job[5] else None,
            "created_at": new_job[6].isoformat() if new_job[6] else None,
            "address": new_job[7],
            "city": new_job[8],  # Добавляем город
            "car": new_job[9],
            "message": "Объявление успешно создано"
        }

        return jsonify(response_data), 200
    except Exception as e:
        Logger.error(f"Error creating job: {str(e)}")
        return jsonify({"error": f"Ошибка при создании вакансии: {str(e)}"}), 500

@filter_router.route("/jobs/filter", methods=["POST"])
@jwt_required()
def filter_jobs():
    """Фильтрация вакансий"""
    try:
        current_user_tg = get_jwt_identity()
        curr_id = FilterDAL.get_finder_id_by_tg(current_user_tg)
        if not curr_id:
            return jsonify({"error": "Пользователь не найден или не существует"}), 404

        data = request.get_json()
        Logger.info(f"Filter request data: {data}")

        wanted_job = data.get("wanted_job")
        address = data.get("address")
        time_start = data.get("time_start")
        time_end = data.get("time_end")
        date = data.get("date")
        salary = data.get("salary")
        salary_to = data.get("salary_to")
        is_urgent = data.get("is_urgent")
        xp = data.get("xp")
        age = data.get("age")
        car = data.get("car")
        city = data.get("city")

        valid_xp = ["нет опыта", "от 1 года", "от 3 лет"]
        valid_age = ["старше 14 лет", "старше 16 лет", "старше 18 лет"]

        if xp is not None and xp not in valid_xp:
            return jsonify({"error": "Недопустимое значение для опыта работы"}), 400

        if age is not None and age not in valid_age:
            return jsonify({"error": "Недопустимое значение для возраста"}), 400

        if car is not None and not isinstance(car, bool):
            return jsonify({"error": "Поле car должно быть булевым (true/false)"}), 400

        if date:
            try:
                if '.' in date:
                    day, month, year = date.split('.')
                    date = f"{year}-{month}-{day}"
            except ValueError:
                return jsonify({"error": "Неверный формат даты. Используйте DD.MM.YYYY или YYYY-MM-DD"}), 400

        if all(v is None for v in [wanted_job, address, time_start, time_end, date, 
                                  salary, salary_to, is_urgent, xp, age, car, city]):
            return jsonify({"error": "Хотя бы один параметр фильтрации должен быть указан"}), 400

        jobs = FilterDAL.get_filtered_jobs(
            wanted_job=wanted_job,
            address=address,
            time_start=time_start,
            time_end=time_end,
            date=date,
            salary=salary,
            salary_to=salary_to,
            is_urgent=is_urgent,
            xp=xp,
            age=age,
            car=car,
            city=city,
            finder_id=curr_id  # Передаем finder_id
        )

        if not jobs:
            return jsonify({"error": "Вакансии не найдены"}), 404

        jobs_json = []
        for job in jobs:
            hours = time_calculate(job[5], job[6]) if job[5] and job[6] else None
            
            job_data = {
                "job_id": job[0],
                "employer_id": job[1],
                "title": job[2],
                "salary": job[3],
                "address": job[4],
                "time_hours": hours,
                "is_favorite": job[7],
                "is_urgent": job[8],
                "created_at": job[9].isoformat() if job[9] else None,
                "rating": job[11],
                "car": job[12],
                "phone": job[13],
                "tg_username": job[14],
                "city": job[15]
            }
            jobs_json.append(job_data)

        return jsonify(jobs_json), 200
    except Exception as e:
        Logger.error(f"Error filtering jobs: {str(e)}")
        return jsonify({"error": f"Ошибка при фильтрации вакансий: {str(e)}"}), 500

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
        if not history:
            return jsonify({"message": "Нет просмотренных вакансий"}), 404

        history_list = []
        for job in history:
            try:
                hours = time_calculate(job[5], job[6]) if len(job) > 6 and job[5] and job[6] else None
                #photo_url = photo_url_convert(job[10])

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
                    #"photo": job[10],
                    "rating": job[11] if len(job) > 11 else None,
                    "car": job[12] if len(job) > 12 else None
                }
                history_list.append(job_data)
            except IndexError as ie:
                Logger.error(f"Ошибка обработки вакансии в истории: {str(ie)}")
                continue

        return jsonify(history_list), 200
    except Exception as e:
        Logger.error(f"Ошибка при получении истории просмотров: {str(e)}")
        return jsonify({
            "message": f"Ошибка при получении истории просмотров: {str(e)}"
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
        "hours": time_calculate(job[4], job[5]) if job[4] and job[5] else None,
        "wanted_job": job[12],
        "user_name": job[13],
        "phone": job[14],
        "tg_username": job[15]
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

        cities = request.args.getlist("cities")  # Получаем список городов из запроса

        jobs = Emplyers_Jobs.get_all_jobs(curr_id, cities)
        if not jobs:
            return jsonify({"error": "Вакансии не найдены"}), 404

        jobs_json = []
        for job in jobs:
            hours = time_calculate(job[7], job[8]) if len(job) > 8 and job[7] and job[8] else None

            job_data = {
                "job_id": job[0],
                "employer_id": job[1],
                "tg_username": job[2],
                "phone": job[3],
                "title": job[4],
                "salary": job[5],
                "address": job[6],
                "time_hours": hours,
                "is_favorite": job[9] if job[9] else False,
                "is_urgent": job[10] if job[10] else False,
                "created_at": job[11].isoformat() if len(job) > 11 and job[11] else None,
                "rating": job[13] if len(job) > 13 else None,
                "car": job[14] if job[14] else False,
                "city": job[15]  # Добавляем город
            }
            jobs_json.append(job_data)

        return jsonify(jobs_json), 200
    except Exception as e:
        Logger.error(f"Ошибка при получении вакансий для работодателя: {str(e)}")
        return jsonify({"message": f"Ошибка при получении вакансий для работодателя: {str(e)}"}), 500

@finder_jobs_router.route("/jobs/finders", methods=["GET"])
@jwt_required()
def get_jobs_for_finders():
    try:
        current_user_tg = get_jwt_identity()
        curr_id = Finder_Jobs.get_finder_id_by_tg(current_user_tg)
        if not curr_id:
            return jsonify({"error": "Пользователь не найден или не существует"}), 404

        cities = request.args.getlist("cities")
        jobs = Finder_Jobs.get_all_jobs(curr_id, cities)
        if not jobs or not jobs[0]:
            return jsonify({"error": "Работа не найдена"}), 404

        jobs_list = []
        for job in jobs:
            hours = time_calculate(job[5], job[6]) if len(job) >= 6 else None

            jobs_list.append({
                "job_id": job[0],
                "employer_id": job[1],
                "title": job[2],
                "salary": job[3],
                "address": job[4],
                "time_hours": hours,
                "is_favorite": job[7],
                "is_urgent": job[8],
                "created_at": job[9].isoformat() if job[9] else None,
                "rating": job[11],
                "car": job[12],
                "phone": job[13],
                "tg_username": job[14],
                "city": job[15]
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
            hours = time_calculate(job[5], job[6]) if len(job) > 6 and job[5] and job[6] else None
            
            job_data = {
                "job_id": job[0],
                "employer_id": job[1],
                "title": job[2],
                "salary": job[3],
                "address": job[4],
                "time_hours": hours,
                "is_urgent": job[7] if job[7] else False,
                "created_at": job[8].isoformat() if len(job) > 8 and job[8] else None,
                "wanted_job": job[9] if len(job) > 9 else None,
                "time_start": job[5].strftime("%H:%M") if len(job) > 5 and isinstance(job[5], time) else None,
                "time_end": job[6].strftime("%H:%M") if len(job) > 6 and isinstance(job[6], time) else None,
                "date": job[10].strftime("%d.%m.%Y") if len(job) > 10 and job[10] else None,
                "xp": job[11] if len(job) > 11 else None,
                "age": job[12] if len(job) > 12 else None,
                "description": job[13] if len(job) > 13 else None,
                "car": job[14] if job[14] else False,
                "city": job[15] if job[15] else None  # Добавляем город
            }
            jobs_list.append(job_data)

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
        Logger.info(f"Updating job {job_id} with data: {data}")

        update_data = {
            "title": data.get("title"),
            "wanted_job": data.get("wanted_job"),
            "description": data.get("description"),
            "salary": data.get("salary"),
            "date": data.get("date"),
            "time_start": data.get("time_start"),
            "time_end": data.get("time_end"),
            "address": data.get("address"),
            "is_urgent": data.get("is_urgent"),
            "xp": data.get("xp"),
            "age": data.get("age"),
            "status": data.get("status"),
            "car": data.get("car"),
            "city": data.get("city")  # Добавляем город
        }

        if all(value is None for value in update_data.values()):
            return jsonify({"error": "Не указаны поля для обновления"}), 400

        if update_data["date"] and '.' in update_data["date"]:
            try:
                day, month, year = update_data["date"].split('.')
                update_data["date"] = f"{year}-{month}-{day}"

                job_date = datetime.strptime(update_data["date"], "%Y-%m-%d").date()
                if job_date < datetime.now().date():
                    return jsonify({"error": "Нельзя указывать прошедшую дату для вакансии"}), 400

                if job_date == datetime.now().date():
                    current_time = datetime.now().time()
                    if data["time_start"]:
                        start_time = datetime.strptime(data["time_start"], "%H:%M").time()
                        if start_time < current_time:
                            return jsonify({"error": "Нельзя указывать прошедшее время для вакансии на сегодня"}), 400
            except ValueError:
                return jsonify({"error": "Неверный формат даты. Используйте DD.MM.YYYY"}), 400

        result = Emplyers_Jobs.update_my_employer_job(
            job_id,
            title=update_data["title"],
            wanted_job=update_data["wanted_job"],
            description=update_data["description"],
            salary=update_data["salary"],
            date=update_data["date"],
            time_start=update_data["time_start"],
            time_end=update_data["time_end"],
            address=update_data["address"],
            is_urgent=update_data["is_urgent"],
            xp=update_data["xp"],
            age=update_data["age"],
            status=update_data["status"],
            car=update_data["car"],
            city=update_data["city"]  # Передаем город
        )

        if result is None:
            return jsonify({"error": "Ошибка при обновлении вакансии"}), 500
        elif result:
            return jsonify({"message": "Вакансия успешно обновлена"}), 200
        else:
            return jsonify({"error": "Не удалось обновить вакансию"}), 400

    except Exception as e:
        Logger.error(f"Error updating job: {str(e)}")
        return jsonify({"error": f"Ошибка при обновлении вакансии: {str(e)}"}), 500
    
@employer_jobs_router.route('/jobs/me/<int:job_id>', methods=["DELETE"])
@jwt_required()
def delete_my_job(job_id):
    """Удаление объявления"""
    try:
        current_user_tg = get_jwt_identity()
        curr_id = Emplyers_Jobs.get_employer_id_by_tg(current_user_tg)
        if not curr_id:
            return jsonify({"error": "Пользователь не найден или не существует"}), 404

        result = Emplyers_Jobs.delete_my_employer_job(job_id, curr_id)
        if result is False:
            return jsonify({"error": "Вакансия не найдена или не принадлежит вам"}), 404

        if result:
            return jsonify({"message": "Вакансия успешно удалена"}), 200
        else:
            return jsonify({"error": "Не удалось удалить вакансию"}), 400
    except Exception as e:
        Logger.error(f"Error deleting job {job_id}: {str(e)}")
        return jsonify({"error": f"Ошибка при удалении вакансии: {str(e)}"}), 500