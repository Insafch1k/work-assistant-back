from werkzeug.datastructures import FileStorage

from project.domain.profile.employer.profile_dal import EmployerProfileDal
from project.utils.data_state import DataState, DataSuccess
from project.utils.image_convertor import save_avatar, delete_avatar, load_and_validate_pillow_image


class EmployerProfileBl:
    @staticmethod
    def get_profile(user_id: str) -> DataState:
        data_state = EmployerProfileDal.get_user(user_id)
        if not data_state:
            return data_state

        data = data_state.data.to_json()
        data_state = EmployerProfileDal.get_resume(user_id)
        if not data_state:
            return data_state

        data['resume'] = data_state.data.to_json()
        return DataSuccess(data)

    @staticmethod
    def change_role(user_id: str) -> DataState:
        data_state = EmployerProfileDal.change_role(user_id, 'finder')

        return data_state

    @staticmethod
    def update_profile(user_id: str, updated_data: dict) -> DataState:
        profile_data = updated_data.get('profile',{})
        resume_data = updated_data.get('resume',{})
        return EmployerProfileDal.update_profile(user_id,resume_data, profile_data)

    @staticmethod
    def update_avatar(user_id: str, avatar: FileStorage) -> DataState:
        img = load_and_validate_pillow_image(avatar.stream)
        avatar_url = save_avatar(img)
        data_state = EmployerProfileDal.update_avatar(user_id, avatar_url)
        if data_state:
            old_photo = data_state.data
            delete_avatar(old_photo)

        return DataSuccess({'new_avatar_url':avatar_url})



    # @staticmethod
    # def get_profile_2(user_id: str) -> dict:
    #     user = EmployerProfileDal.get_user_2(user_id)
    #     resume = EmployerProfileDal.get_resume_2(user_id)
    #     data = user.to_json()
    #     data['resume'] = resume.to_json()
    #     return data
