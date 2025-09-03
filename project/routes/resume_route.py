from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from project.DAL.resume_dal import ResumeDAL
from project.BL.resume_bl import form_response

resume_router = Blueprint("resume_router", __name__)


@resume_router.route('/resumes', methods=['POST'])
@jwt_required()
def create_resume():
    """Создание нового резюме"""
    current_user_tg = get_jwt_identity()
    curr_id = ResumeDAL.get_user_id_by_tg(current_user_tg)
    if not curr_id:
        return jsonify({"error": "Пользователь не найден"}), 404

    data = request.get_json()
    #resume_data = ResumeCreate(**data)

    resume = ResumeDAL.create_resume(curr_id, data["job_title"], data["education"], data["work_xp"], data["skills"])

    print(resume)
    return jsonify(form_response(resume)), 200


@resume_router.route('/resumes/<int:resume_id>', methods=['DELETE'])
@jwt_required()
def delete_resume(resume_id):
    """Удаление резюме"""
    current_user_tg = get_jwt_identity()
    resume = ResumeDAL.check_resume(resume_id, current_user_tg)

    if not resume:
        return jsonify({"error": "Резюме не найдено или доступ запрещён"}), 404

    ResumeDAL.delete_resume(resume_id)
    return jsonify({"message": "Резюме удалено"}), 200


@resume_router.route('/resumes', methods=['GET'])
@jwt_required()
def get_user_resumes():
    """Получение всех активных резюме пользователя"""
    current_user_tg = get_jwt_identity()

    resume = ResumeDAL.get_resume_data(current_user_tg)
    return jsonify(resume), 200
