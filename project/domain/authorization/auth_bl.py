import io
import string

from flask import render_template
from flask_mail import Message
from werkzeug.security import generate_password_hash

from project import settings
from project.application.entities.user import User
from project.application.routes.authorization.auth_schemas import LoginValidateSchema, RegisterTgValidateSchema, \
    LoginTgValidateSchema, RegistrationValidateSchema, ConfirmationValidateSchema, ForgotPasswordValidateSchema, \
    RecoveryPasswordValidateSchema, ChangePasswordValidateSchema
from project.domain.authorization.auth_dal import AuthDal
from project.utils.data_state import DataState, DataFailedMessage, DataSuccess
import secrets

from project.utils.image_convertor import download_image_bytes, save_avatar, load_and_validate_pillow_image


def generate_secure_code(length: int = 4) -> str:
    """Генерирует криптографически безопасный код"""
    return ''.join(secrets.choice(string.digits) for _ in range(length))

class AuthBl:
    @staticmethod
    def register_tg(data: RegisterTgValidateSchema) -> DataState[User]:
        data_state = AuthDal.add_tg_user(data.tg_id, data.tg_username, data.user_name, data.user_role)
        if data_state and data.avatar_url:
            try:
                photo_arr = download_image_bytes(data.avatar_url)
                bio = io.BytesIO(photo_arr)
                img = load_and_validate_pillow_image(bio)
                avatar_url = save_avatar(img)
                AuthDal.set_avatar(data_state.data.id,avatar_url)
            except Exception as ex:
                DataFailedMessage(f"Ошибка при добавлении фото пользователя" ,error=ex)

        return data_state

    @staticmethod
    def update_user(data: LoginTgValidateSchema) -> DataState[User]:
        return AuthDal.update_user(data.tg_id, data.tg_username)

    @staticmethod
    def forgot_password(data: ForgotPasswordValidateSchema) -> DataState:
        data_state = AuthDal.email_exists(data.email)
        if not data_state:
             return data_state
        user = data_state.data
        if not user:
            return DataFailedMessage("Аккаунта с такой почтой не существует")

        temporary_id = generate_secure_code()
        mail_code = generate_secure_code()
        final_code = f'{temporary_id}{mail_code}'

        data_state = AuthDal.store_password_recovery_code(final_code, user.id)
        if not data_state:
            return data_state

        email_data_state = AuthBl.send_email(mail_code, data.email,'reset_password')
        if not email_data_state:
            return email_data_state

        return DataSuccess(int(temporary_id))

    @staticmethod
    def check_user(data: LoginValidateSchema) -> DataState[User]:
        return AuthDal.check_user(data.email, data.password)

    @staticmethod
    def register_mail(data: RegistrationValidateSchema) -> DataState[int]:
        email_data_state = AuthDal.email_exists(data.email)
        if not email_data_state:
            return email_data_state

        user = email_data_state.data
        if user:
            return DataFailedMessage("Аккаунт с такой почтой уже существует")

        temporary_id = generate_secure_code()
        mail_code = generate_secure_code()
        final_code= f'{temporary_id}{mail_code}'
        pwd_hash = generate_password_hash(data.password)
        verif_data_state = AuthDal.store_verification_data(final_code, data.email, pwd_hash, data.username, data.user_role)
        if not verif_data_state:
            return verif_data_state

        email_data_state = AuthBl.send_email(mail_code, data.email,'email_confirmation')
        if not email_data_state:
            return email_data_state

        return DataSuccess(int(temporary_id))

    @staticmethod
    def add_websocket_uid(user_id, uid) -> DataState:
        return AuthDal.add_websocket_uid(user_id, uid)

    @staticmethod
    def delete_websocket_uid(user_id) -> DataState:
        return AuthDal.delete_websocket_uid(user_id)

    @staticmethod
    def add_token(user_id, jti) -> DataState:
        return AuthDal.add_token(user_id, jti)

    @staticmethod
    def has_token(user_id, jti) -> DataState:
        return AuthDal.has_token(user_id, jti)

    @staticmethod
    def delete_token(user_id, jti) -> DataState:
        return AuthDal.delete_token(user_id, jti)

    @staticmethod
    def delete_all_sessions(user_id) -> DataState:
        return AuthDal.delete_all_sessions(user_id)

    @staticmethod
    def confirm_mail(result: ConfirmationValidateSchema) -> DataState[User]:
        final_code=f'{result.temporary_id}{result.code}'
        verif_data_state = AuthDal.get_verification_data(final_code)
        if not verif_data_state:
            return verif_data_state

        user = verif_data_state.data
        email_data_state = AuthDal.email_exists(user.email)
        if not email_data_state:
            return email_data_state

        if email_data_state.data:
            return DataFailedMessage("Аккаунт с такой почтой уже существует")

        add_data_state = AuthDal.add_email_user(user)
        if not add_data_state:
            return add_data_state

        return DataSuccess(add_data_state.data)

    @staticmethod
    def check_recovery_code(result: ConfirmationValidateSchema) -> DataState:
        final_code=f'{result.temporary_id}{result.code}'
        verif_data_state = AuthDal.check_password_recovery_code(final_code)

        return verif_data_state

    @staticmethod
    def recovery_password(result: RecoveryPasswordValidateSchema) -> DataState:
        final_code = f'{result.temporary_id}{result.code}'
        pwd_hash = generate_password_hash(result.password)
        verif_data_state = AuthDal.check_password_recovery_code(final_code,delete_after=True)
        if not verif_data_state:
            return verif_data_state

        user_id = verif_data_state.data
        pwd_data_state = AuthDal.recovery_password(user_id, pwd_hash)
        return pwd_data_state

    @staticmethod
    def change_password(result: ChangePasswordValidateSchema,user_id) -> DataState:
        new_pwd_hash = generate_password_hash(result.new_password)
        return AuthDal.change_password(user_id, result.old_password, new_pwd_hash)



    @staticmethod
    def send_email(code, email, message_type):
        try:
            message_types = {'email_confirmation': ["Подтвердите ваш email",'email_confirmation.html'],
                             'reset_password': ['Сброс пароля','password_reset.html']}
            mail_name, mail_template = message_types[message_type]
            msg = Message(
                mail_name,
                recipients=[email],
                html=render_template(
                    mail_template,
                    code=code,
                    expires=settings.CODE_EXPIRES
                )
            )
            from project import mail

            mail.send(msg)
            return DataSuccess()
        except Exception as ex:
            return DataFailedMessage('Не удалось отправить письмо на почту!',error=ex)