from project.application.entities.user import User
from project.domain.authorization.auth_dal import AuthDal
from project.utils.data_state import DataState, DataSuccess


class AuthBl:
    @staticmethod
    def add_user(tg_id, tg_username,user_name, user_role) -> DataState[User]:
        return AuthDal.add_user(tg_id, tg_username,user_name, user_role)

    @staticmethod
    def update_user(tg_id, tg_username) -> DataState[User]:
        return AuthDal.update_user(tg_id, tg_username)