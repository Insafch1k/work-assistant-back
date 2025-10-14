from project.domain.core.exceptions import DataBaseError
from project.domain.profile.base_profile_dal import BaseProfileDal
from project.utils.data_state import DataState


def get_user_role(user_id) -> str:
    user_data_state = BaseProfileDal.get_user(user_id)
    if user_data_state:
        return user_data_state.data.user_role

    raise DataBaseError(user_data_state.error_details)