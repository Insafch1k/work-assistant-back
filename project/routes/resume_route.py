from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from project.DAL.resume_dal import ResumeDAL

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

    return jsonify({
        "resume_id": resume[0],
        "user_id": resume[1],
        "job_title": resume[2],
        "education": resume[3],
        "work_xp": resume[4],
        "skills": resume[5],
        "is_active": resume[6]
    }), 200


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


@resume_router.route('/resumes/<int:resume_id>', methods=['PUT'])
@jwt_required()
def update_resume(resume_id):
    """Редактирование резюме"""
    current_user_tg = get_jwt_identity()
    resume = ResumeDAL.check_resume(resume_id, current_user_tg)
    if not resume:
        return jsonify({"error": "Резюме не найдено или доступ запрещён"}), 404

    data = request.get_json()

    resume = ResumeDAL.update_resume(resume_id, data["job_title"], data["education"], data["work_xp"], data["skills"])

    return jsonify({
        "resume_id": resume[0],
        "job_title": resume[1],
        "education": resume[2],
        "work_xp": resume[3],
        "skills": resume[4]
    }), 200


@resume_router.route('/resumes', methods=['GET'])
@jwt_required()
def get_user_resumes():
    """Получение всех активных резюме пользователя"""
    current_user_tg = get_jwt_identity()

    resume = ResumeDAL.get_resume_data(current_user_tg)
    return jsonify({
                "resume_id": resume[0],
                "user_id": resume[1],
                "job_title": resume[2],
                "education": resume[3],
                "work_xp": resume[4],
                "skills": resume[5],
                "created_at": resume[6].isoformat(),
                "is_active": resume[7]
            }), 200