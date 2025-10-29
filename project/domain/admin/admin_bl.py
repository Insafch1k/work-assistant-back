from typing import Optional
from project.application.entities.user import User
from project.domain.admin.admin_dal import AdminDal
from project.domain.authorization.auth_bl import AuthBl
from project.utils.data_state import DataState


class AdminBl:
    @staticmethod
    def is_admin(user_id: int) -> DataState[bool]:
        return AdminDal.is_admin(user_id)

    @staticmethod
    def set_ban_status(user_id: int,is_banned: bool) -> DataState[bool]:
        if is_banned:
            token_data_state = AuthBl.delete_all_sessions(user_id=user_id)
            if not token_data_state:
                return token_data_state.to_response()

        return AdminDal.set_ban_status(user_id, is_banned)

    @staticmethod
    def get_users_by_name(result) ->  DataState[list[User]]:
        return AdminDal.get_users_by_name(result.offset, result.limit,result.name_filter)