from project.domain.profile.employer.profile_dal import EmployerProfileDal
from project.utils.data_state import DataState, DataSuccess


class EmployerProfileBl:
    @staticmethod
    def get_profile_1(user_id: str) -> DataState:
        data_state = EmployerProfileDal.get_user_1(user_id)
        if not data_state:
            return data_state

        data = data_state.data.to_json()
        data_state = EmployerProfileDal.get_resume_1(user_id)
        if not data_state:
            return data_state

        data['resume'] = data_state.data.to_json()
        return DataSuccess(data)

    @staticmethod
    def get_profile_2(user_id: str) -> dict:
        user = EmployerProfileDal.get_user_2(user_id)
        resume = EmployerProfileDal.get_resume_2(user_id)
        data = user.to_json()
        data['resume'] = resume.to_json()
        return data
