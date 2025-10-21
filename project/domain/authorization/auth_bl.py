import string
from flask import render_template
from flask_mail import Message
from werkzeug.security import generate_password_hash

from project import settings
from project.application.entities.user import User
from project.application.routes.authorization.auth_schemas import LoginValidateSchema, RegisterTgValidateSchema, \
    LoginTgValidateSchema, RegistrationValidateSchema
from project.domain.authorization.auth_dal import AuthDal
from project.utils.data_state import DataState, DataFailedMessage, DataSuccess
import secrets

def generate_secure_code(length: int = 4) -> str:
    """Генерирует криптографически безопасный код"""
    return ''.join(secrets.choice(string.digits) for _ in range(length))

class AuthBl:
    @staticmethod
    def register_tg(data: RegisterTgValidateSchema) -> DataState[User]:
        return AuthDal.add_tg_user(data.tg_id, data.tg_username, data.user_name, data.user_role)

    @staticmethod
    def update_user(data: LoginTgValidateSchema) -> DataState[User]:
        return AuthDal.update_user(data.tg_id, data.tg_username)

    @staticmethod
    def check_user(data: LoginValidateSchema) -> DataState[User]:
        return AuthDal.check_user(data.email, data.password)

    @staticmethod
    def register_mail(data: RegistrationValidateSchema) -> DataState[int]:
        email_data_state = AuthDal.email_exists(data.email)
        if not email_data_state:
            return email_data_state

        temporary_id = generate_secure_code()
        mail_code = generate_secure_code()
        final_code= f'{temporary_id}{mail_code}'
        pwd_hash = generate_password_hash(data.password)
        verif_data_state = AuthDal.store_verification_data(final_code, data.email, pwd_hash, data.username, data.user_role)
        if not verif_data_state:
            return verif_data_state

        email_data_state = AuthBl.send_confirmation_email(mail_code, data.email)
        if not email_data_state:
            return email_data_state

        return DataSuccess(int(temporary_id))

    @staticmethod
    def confirm_mail(temporary_id, code) -> DataState[User]:
        final_code=f'{temporary_id}{code}'
        verif_data_state = AuthDal.get_verification_data(final_code)
        if not verif_data_state:
            return verif_data_state

        user = verif_data_state.data
        add_data_state = AuthDal.add_email_user(user)
        if not add_data_state:
            return add_data_state

        return DataSuccess(add_data_state.data)

    @staticmethod
    def send_confirmation_email(code, email):
        try:

            msg = Message(
                "Подтвердите ваш email",
                recipients=[email],
                html=render_template(
                    'email_confirmation.html',
                    code=code,
                    expires=settings.CODE_EXPIRES
                )
            )
            from project import mail

            mail.send(msg)
            return DataSuccess()
        except Exception as ex:
            return DataFailedMessage('Не удалось отправить письмо на почту!',error=ex)