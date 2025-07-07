from project.utils.logger import Logger
from project.DAL.auth_dal import AuthDAL


def validate_register(data):
    try:
        ret = {"status": "access"}
        if not data or not data["user_role"] or not data["user_name"]:
            ret = {
                "status": "error",
                "error": "Неправильно заполнены поля"
            }
            return ret
        if AuthDAL.check_user(data["tg"]):
            ret = {
                "status": "error",
                "error": "Пользователь уже существует"
            }
            return ret
        return ret
    except Exception as e:
        Logger.error(f"Error validate register {str(e)}")
        raise


def get_user_data(temp_data):
    return {
        "user_id": temp_data[0],
        "tg": temp_data[1],
        "user_role": temp_data[2],
        "user_name": temp_data[3],
        "rating": float(temp_data[4])
    }
