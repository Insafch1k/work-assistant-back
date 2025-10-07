from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token

from project.BL.metrics_bl import MetricsBL
from project.utils.logger import Logger
from project.DAL.auth_dal import AuthDAL
from project.BL.auth_bl import validate_register, get_user_data
from project.utils.metric_events import MetricEvents

auth_router = Blueprint("auth_router", __name__)

@auth_router.route("/mobile/register", methods=['POST'])
def register():
    """
    Регистрация пользователя
    {
        username: str
        email: str
        password: str
    }
    :return:
    """
    try:
        json_data = request.get_json()

        if AuthorizationDal.email_exists(email):
            result = {
                "status": "error",
                "message": "This email already exists"
            }

        pwd_hash = generate_password_hash(password)
        id_user = AuthorizationDal.create_user(username, pwd_hash)
        if not id_user:
            return {
                "status": "error",
                "message": "Error create user"
            }
        AuthorizationBl.send_confirmation_email(email, id_user)

        # access_token = create_access_token(identity=id_user)

        result = {
            "status": "success"
        }

        if result["status"] == "error":
            return jsonify(result), 400

        return jsonify(result), 200
    except Exception as e:
        Logger.error(f"Error register {str(e)}")
        return jsonify({
            "Error": f"Error register {str(e)}"
        }), 500

@auth_router.route('/confirm-email', methods=['GET'])
def confirm_email():
    """
    Подтверждение почты
    :return:
    """
    try:
        token = request.args.get('token')

        if not token:
            return jsonify({"error": "Missing token"}), 400

        email, id_user = AuthorizationBl.confirm_token(token)

        if not email:
            return jsonify({"error": "Invalid or expired token"}), 400

        result = AuthorizationBl.confirm_user(email, id_user)
        if result['status'] == "error":
            return jsonify(result), 500

        result_create_balances = AuthorizationBl.create_balances(id_user)
        if result_create_balances['status'] == 'error':
            return jsonify(result), 500
        return jsonify(result), 200
    except Exception as e:
        Logger.error(f"Error register {str(e)}")
        return jsonify({
            "Error": f"Error register {str(e)}"
        }), 500


@auth_router.route('/mobile/login', methods=['POST'])
def login():
    try:
        json_data = request.get_json()
        data, errors = LoginValidateSchema.from_request(json_data)

        if errors is not None:
            return jsonify({"error": errors}), 400

        result, code = AuthorizationBl.login(data.email, data.password)
        # if result["status"] == "error":
        return jsonify(result), code
    except Exception as e:
        Logger.error(f"Error login {str(e)}")
        return jsonify({
            "Error": f"Error login {str(e)}"
        }), 500

@auth_router.route("/profile/init", methods=["POST"])
def register_tg():
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
        AuthDAL.add_finder(list(user.values())[0])
        AuthDAL.add_employer(list(user.values())[0])
        MetricsBL.track_metric(MetricEvents.UserRegistered, user['user_id'])
        access_token = create_access_token(identity=str(user['user_id']))
        return jsonify({
            "message": "Вы успешно зарегистрированы",
            "access_token": access_token
        }), 200
    except Exception as e:
        Logger.error(f"Error register {str(e)}")
        return jsonify({
            "message": f"Error register {str(e)}"
        }), 500

@auth_router.route("/profile/login", methods=["PATCH"])
def login():
    """
    Авторизация пользователей
    :return:
    """
    try:
        data = request.get_json()

        user = AuthDAL.get_user_by_tg(data["tg"])
        if not user:
            return jsonify({"message": "Пользователь не найден"}), 404

        update_data = {}

        if user[3] != data["user_role"]:
            update_data["user_role"] = data["user_role"]

        if user[2] != data["tg_username"]:
            update_data["tg_username"] = data["tg_username"]

        update_data["last_login_at"] = datetime.now()

        if update_data:
            AuthDAL.update_user(data["tg"], **update_data)
            print(update_data)

        access_token = create_access_token(identity=str(user['user_id']))
        return jsonify({
            "message": "Вы успешно авторизовались",
            "access_token": access_token
        }), 200
    except Exception as e:
        Logger.error(f"Error login {str(e)}")
        return jsonify({
            "message": f"Error login {str(e)}"
        }), 500