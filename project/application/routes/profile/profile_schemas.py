from __future__ import annotations
from typing import Optional
from loguru import logger
from pydantic import BaseModel, ValidationError

from project.utils.data_state import DataState, DataSuccess, DataFailedMessage


class UpdateResumeSchema(BaseModel):
    job_title: Optional[str] = None
    education: Optional[str] = None
    work_xp: Optional[str] = None
    skills: Optional[str] = None

    @staticmethod
    def from_request(json_data: dict) -> DataState[UpdateResumeSchema]:
        try:
            return DataSuccess(UpdateResumeSchema(**json_data))
        except ValidationError as e:
            errors = [
                {"field": err["loc"][0], "message": err["msg"]}
                for err in e.errors()
            ]
            return DataFailedMessage(f'Ошибка валидации резюме: {errors}',error=e)


class UpdateProfileSchema(BaseModel):
    user_name: Optional[str] = None
    phone: Optional[str] = None
    photo: Optional[str] = None
    resume: Optional[UpdateResumeSchema] = None

    @staticmethod
    def from_request(json_data: dict) -> DataState[UpdateProfileSchema]:
        try:
            # Обрабатываем вложенный объект resume
            if 'resume' in json_data and isinstance(json_data['resume'], dict):
                json_data['resume'] = UpdateResumeSchema(**json_data['resume'])
            return DataSuccess(UpdateProfileSchema(**json_data))
        except ValidationError as e:
            errors = [
                {"field": err["loc"][0], "message": err["msg"]}
                for err in e.errors()
            ]
            return DataFailedMessage(f'Ошибка валидации профиля: {errors}',error=e)

    def get_update_fields(self) -> dict:
        """Возвращает только те поля, которые были переданы для обновления"""
        profile_data = {}
        update_data = {}
        if self.user_name is not None:
            profile_data['user_name'] = self.user_name
        if self.phone is not None:
            profile_data['phone'] = self.phone
        if self.photo is not None:
            profile_data['photo'] = self.photo
        if len(profile_data) != 0:
            update_data['profile'] = profile_data
        if self.resume is not None:
            update_data['resume'] = {
                'job_title': self.resume.job_title,
                'education': self.resume.education,
                'work_xp': self.resume.work_xp,
                'skills': self.resume.skills
            }

        return update_data