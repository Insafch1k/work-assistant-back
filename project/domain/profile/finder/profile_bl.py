from project.domain.profile.finder.profile_dal import FinderProfileDal
from project.utils.data_state import DataState, DataSuccess


class FinderProfileBl:
    @staticmethod
    def get_profile(user_id: str) -> DataState:
        data_state = FinderProfileDal.get_user(user_id)
        if not data_state:
            return data_state

        data = data_state.data.to_json()
        return DataSuccess(data)

    @staticmethod
    def change_role(user_id: str) -> DataState:
        data_state = FinderProfileDal.change_role(user_id, 'employer')

        return data_state
