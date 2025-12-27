from werkzeug.datastructures import FileStorage

from project.domain.profile.employer.profile_dal import EmployerProfileDal
from project.domain.profile.finder.profile_dal import FinderProfileDal
from project.utils.data_state import DataState, DataSuccess
from project.utils.image_convertor import save_avatar, delete_avatar, load_and_validate_pillow_image


class FinderProfileBl:
    @staticmethod
    def get_profile(user_id: str) -> DataState:
        data_state = FinderProfileDal.get_user(user_id)
        if not data_state:
            return data_state

        data = data_state.data.to_json()
        return DataSuccess(data)

    @staticmethod
    def update_avatar(user_id: str, avatar: FileStorage) -> DataState:
        img = load_and_validate_pillow_image(avatar.stream)
        avatar_url = save_avatar(img)
        data_state = EmployerProfileDal.update_avatar(user_id, avatar_url)
        if data_state:
            old_photo = data_state.data
            delete_avatar(old_photo)

        return data_state

    @staticmethod
    def change_role(user_id: str) -> DataState:
        data_state = FinderProfileDal.change_role(user_id, 'employer')

        return data_state
