from project.utils.logger import Logger
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token

from project.DAL.auth_dal import AuthDAL
from project.BL.auth_bl import validate_register, get_user_data

auth_router = Blueprint("auth_router", __name__)


@auth_router.route("/profile/init", methods=["POST"])
def register():
    """
    Регистрация пользователей
    :return:
    """
    try:
        data = request.get_json()
        result = validate_register(data)

        if result["status"] == "error":
            return jsonify(result), 400

        temp_data = AuthDAL.add_user(data["tg"], data["tg_username"], data["user_role"], data["user_name"])
        user = get_user_data(temp_data)
        if data["user_role"] == "finder":
            AuthDAL.add_finder(list(user.values())[0])
        if data["user_role"] == "employer":
            AuthDAL.add_employer(list(user.values())[0])


        access_token = create_access_token(identity=str(data["tg"]))
        return jsonify({
            "message": "Вы успешно зарегистрированы",
            "access_token": access_token
        }), 200
    except Exception as e:
        Logger.error(f"Error register {str(e)}")
        return jsonify({
            "message": f"Error register {str(e)}"
        }), 500

@auth_router.route("/profile/login", methods=["GET"])
def login():
    """
    Авторизация пользователей
    :return:
    """
    try:
        data = request.get_json()
        access_token = create_access_token(identity=str(data["tg"]))
        return jsonify({
            "message": "Вы успешно авторизовались",
            "access_token": access_token
        }), 200
    except Exception as e:
        Logger.error(f"Error login {str(e)}")
        return jsonify({
            "message": f"Error login {str(e)}"
        }), 500