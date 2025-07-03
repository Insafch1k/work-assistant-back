from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from project.DAL.resume_dal import ResumeDAL

resume_router = Blueprint("resume_router", __name__)


@resume_router.route('/resumes', methods=["POST"])
@jwt_required()
def create_resume():
    """Создание нового резюме"""
    current_user_tg = get_jwt_identity()
    curr_id = ResumeDAL.get_user_id_by_tg(current_user_tg)
    if not curr_id:
        return jsonify({"error": "Пользователь не найден"}), 404

    data = request.get_json()

    resume = ResumeDAL.create_resume(curr_id, data["job_title"], data["education"], data["work_xp"], data["skills"])
    print(resume)

    return jsonify({
        "resume_id": resume[0],
        "user_id": resume[1],
        "job_title": resume[2],
        "education": resume[3],
        "work_xp": resume[4],
        "skills": resume[5]
    }), 200


@resume_router.route('/resumes/<int:resume_id>', methods=["DELETE"])
@jwt_required()
def delete_resume(resume_id):
    """Удаление резюме"""
    current_user_tg = get_jwt_identity()
    curr_id = ResumeDAL.get_finder_id_by_tg(current_user_tg)
    if not curr_id:
        return jsonify({"error": "Пользователь не найден или не существует"}), 404

    resume_id = ResumeDAL.get_resume_id_by_finder(curr_id)
    if not resume_id:
        return jsonify({"error": "Резюме не найдено или доступ запрещён"}), 404

    ResumeDAL.delete_resume(resume_id)
    return jsonify({"message": "Резюме удалено"}), 200


@resume_router.route('/resumes/me', methods=["PATCH"])
@jwt_required()
def update_resume():
    """Редактирование резюме"""
    current_user_tg = get_jwt_identity()
    curr_id = ResumeDAL.get_finder_id_by_tg(current_user_tg)
    if not curr_id:
        return jsonify({"error": "Пользователь не найден или не существует"}), 404

    resume_id = ResumeDAL.get_resume_id_by_finder(curr_id)
    if not resume_id:
        return jsonify({"error": "Резюме не найдено"}), 404

    data = request.get_json()
    temp_json = {"job_title": None, "education": None, "work_xp": None, "skills": None}

    for temp in temp_json:
        if temp in data:
            temp_json[temp] = data[temp]
            if temp == "skills":
                temp_json[temp] = data[temp].split(',') if data[temp] else []


    resume = ResumeDAL.update_resume(resume_id, job_title=temp_json["job_title"], education=temp_json["education"],
                                     work_xp=temp_json["work_xp"], skills=temp_json["skills"])
    print({
        "resume_id": resume[0],
        "job_title": resume[1],
        "education": resume[2],
        "work_xp": resume[3],
        "skills": resume[4]
    })

    if resume:
        return jsonify({"message": "Резюме обновлёно"}), 200
    return jsonify({"error": "Резюме не получилось обновить"})


@resume_router.route('/resumes', methods=["GET"])
@jwt_required()
def get_user_resumes():
    """Получение всех активных резюме пользователя"""
    current_user_tg = get_jwt_identity()

    resume = ResumeDAL.get_resume_data(current_user_tg)
    return jsonify({
                "job_title": resume[0],
                "education": resume[1],
                "work_xp": resume[2],
                "skills": resume[3]
            }), 200