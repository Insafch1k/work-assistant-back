import json
from datetime import datetime, timedelta

import redis
from loguru import logger
from werkzeug.security import check_password_hash

from project import settings
from project.application.entities.user import User
from project.domain.core.models.resume import ResumeModel
from project.domain.core.models.user import UserModel
from project.utils.data_state import DataState, DataFailedMessage, DataSuccess
from project.utils.db_connection import connection_db, connection_redis


class AuthDal:
    @staticmethod
    def add_tg_user(tg_id, tg_username, user_name, user_role) -> DataState[User]:
        Session = connection_db()
        if not Session:
            return DataFailedMessage("Database connection error")

        with Session() as session:
            try:
                user = session.query(UserModel).filter(UserModel.tg_id == tg_id).first()
                if user:
                    return DataFailedMessage("Пользователь уже существует",code=406)
                user = UserModel(
                    user_role=user_role,
                    tg_username=tg_username,
                    tg_id=tg_id,
                    user_name=user_name,
                    auth_method='telegram')
                session.add(user)
                session.flush() # Синхронизирует состояние сессии с БД  Все изменения в сессии перенесутся в БД, но не зафиксируются
                resume = ResumeModel(
                    user_id=user.id)
                session.add(resume)
                session.commit()

                logger.info(f"TG Пользователь {user.user_name} успешно добавлен с ID: {user.id}")
                return DataSuccess(User.model_validate(user))
            except Exception as e:
                session.rollback()
                return DataFailedMessage(f"Ошибка при добавлении пользователя",error=e)

    @staticmethod
    def add_email_user(user: User) -> DataState[User]:
        Session = connection_db()
        if not Session:
            return DataFailedMessage("Database connection error")

        with Session() as session:
            try:
                user = UserModel(
                    user_role=user.user_role,
                    email=user.email,
                    password_hash=user.password_hash,
                    user_name=user.user_name,
                    auth_method='email')
                session.add(user)
                session.flush() # Синхронизирует состояние сессии с БД  Все изменения в сессии перенесутся в БД, но не зафиксируются
                resume = ResumeModel(
                    user_id=user.id)
                session.add(resume)
                session.commit()

                logger.debug(f"Пользователь {user.user_name} успешно добавлен с ID: {user.id}")
                return DataSuccess(User.model_validate(user))
            except Exception as e:
                session.rollback()
                return DataFailedMessage(f"Ошибка при добавлении пользователя",error=e)

    @staticmethod
    def add_websocket_uid(user_id, uid) -> DataState:
        try:
            redis_client = connection_redis()
            if not redis_client:
                return DataFailedMessage("Redis Database connection error")

            key = f"active_users:{user_id}"
            redis_client.setex(key, timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRES), uid)
            return DataSuccess()
        except Exception as e:
            return DataFailedMessage(f"Ошибка при добавлении websocket_uid",error=e)

    @staticmethod
    def delete_websocket_uid(user_id: str) -> DataState:
        try:
            redis_client = connection_redis()
            if not redis_client:
                return DataFailedMessage("Redis Database connection error")

            key = f"active_users:{user_id}"
            redis_client.delete(key)
            return DataSuccess()
        except Exception as e:
            return DataFailedMessage(f"Ошибка при удалении websocket_uid",error=e)


    @staticmethod
    def add_token(user_id, jti) -> DataState:
        try:
            redis_client = connection_redis()
            if not redis_client:
                return DataFailedMessage("Redis Database connection error")

            key = f"tokens:{user_id}"
            redis_client.sadd(key, jti)
            redis_client.expire(key, timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRES))
            return DataSuccess()
        except Exception as e:
            return DataFailedMessage(f"Ошибка при добавлении токена",error=e)

    @staticmethod
    def has_token(user_id: str, jti: str) -> DataState:
        try:
            redis_client = connection_redis()
            if not redis_client:
                return DataFailedMessage("Redis Database connection error")

            key = f"tokens:{user_id}"
            return DataSuccess(redis_client.sismember(key, jti))
        except Exception as e:
            return DataFailedMessage(f"Ошибка при проверке токена",error=e)

    @staticmethod
    def delete_token(user_id: str, jti: str) -> DataState:
        try:
            redis_client = connection_redis()
            if not redis_client:
                return DataFailedMessage("Redis Database connection error")

            key = f"tokens:{user_id}"
            redis_client.srem(key, jti)
            if redis_client.scard(key) == 0:  # если нет больше токенов
                redis_client.delete(key)
            return DataSuccess()
        except Exception as e:
            return DataFailedMessage(f"Ошибка при удалении токена",error=e)

    @staticmethod
    def delete_all_sessions(user_id: str) -> DataState:
        try:
            redis_client = connection_redis()
            if not redis_client:
                return DataFailedMessage("Redis Database connection error")

            key = f"tokens:{user_id}"
            redis_client.delete(key)
            return DataSuccess()
        except Exception as e:
            return DataFailedMessage(f"Ошибка при удалении всех токенов пользователя",error=e)

    @staticmethod
    def store_verification_data(code, email, password_hash, user_name, user_role) -> DataState:
        try:
            redis_client = connection_redis()
            if not redis_client:
                return DataFailedMessage("Redis Database connection error")

            verification_data = {
                'user_name': user_name,
                'email': email,
                'password_hash': password_hash,  # Всегда храним хеш!
                'user_role': user_role,
            }

            # Сохраняем в Redis
            key = f"verification:{code}"
            redis_client.setex(
                key,
                timedelta(minutes=settings.CODE_EXPIRES),
                json.dumps(verification_data)
            )

            logger.debug(f"Пользователь {user_name} ожидает подтверждение почты")
            return DataSuccess()
        except Exception as e:
            return DataFailedMessage(f"Ошибка при сохранении кода",error=e)

    @staticmethod
    def get_verification_data(code) -> DataState:
        try:
            redis_client = connection_redis()
            if not redis_client:
                return DataFailedMessage("Redis Database connection error")

            key = f"verification:{code}"
            data = redis_client.get(key)
            if data:
                redis_client.delete(key)  # удаляем код после подтврждения
                return DataSuccess(User.model_validate(json.loads(data)))

            return DataFailedMessage('Неверный или просроченный код подтверждения',code=400)
        except Exception as e:
            return DataFailedMessage(f"Ошибка при проверке кода",error=e)

    @staticmethod
    def check_password_recovery_code(code,delete_after: bool=False) -> DataState[str]:
        try:
            redis_client = connection_redis()
            if not redis_client:
                return DataFailedMessage("Redis Database connection error")

            key = f"verification:{code}"
            user_id = redis_client.get(key)
            if not user_id:
                return DataFailedMessage('Неверный или просроченный код подтверждения',code=400)
            if delete_after:
                redis_client.delete(key)

            return DataSuccess(user_id.decode('utf-8'))

        except Exception as e:
            return DataFailedMessage(f"Ошибка при проверке кода",error=e)

    @staticmethod
    def store_password_recovery_code(code, user_id) -> DataState:
        try:
            redis_client = connection_redis()
            if not redis_client:
                return DataFailedMessage("Redis Database connection error")

            # Сохраняем в Redis
            key = f"verification:{code}"
            redis_client.setex(
                key,
                timedelta(minutes=settings.CODE_EXPIRES),
                user_id
            )

            return DataSuccess()
        except Exception as e:
            return DataFailedMessage(f"Ошибка при сохранении кода",error=e)



    @staticmethod
    def update_user(tg_id, tg_username) -> DataState[User]:
        Session = connection_db()
        if not Session:
            return DataFailedMessage("Database connection error")

        with Session() as session:
            try:
                user = session.query(UserModel).filter(UserModel.tg_id == tg_id).first()
                if not user:
                    return DataFailedMessage("Пользователь не найден",code=404)

                if user.banned:
                    return DataFailedMessage("Пользователь заблокирован",code=423)

                user.tg_username = tg_username
                user.last_login_at = datetime.now()
                session.commit()

                #logger.info(f"Пользователь {user.user_name} успешно вошел в аккаунт")
                return DataSuccess(User.model_validate(user))
            except Exception as e:
                session.rollback()
                return DataFailedMessage(f"Ошибка при обновлении пользователя",error=e)

    @staticmethod
    def recovery_password(user_id, psw_hash) -> DataState[User]:
        Session = connection_db()
        if not Session:
            return DataFailedMessage("Database connection error")

        with Session() as session:
            try:
                user = session.get(UserModel, user_id)
                if not user:
                    return DataFailedMessage("Пользователь не найден")

                user.password_hash = psw_hash
                session.commit()

                logger.debug(f"Пользователь {user.user_name} успешно восстановил аккаунт и сменил пароль")
                return DataSuccess(User.model_validate(user))
            except Exception as e:
                session.rollback()
                return DataFailedMessage(f"Ошибка при смене пароля",error=e)

    @staticmethod
    def check_user(email, password) -> DataState[User]:
        Session = connection_db()
        if not Session:
            return DataFailedMessage("Database connection error")

        with Session() as session:
            try:
                user = session.query(UserModel).filter(UserModel.email == email).first()
                if not user:
                    return DataFailedMessage("Пользователь не найден")

                if not check_password_hash(user.password_hash,password):
                    return DataFailedMessage("Неверный пароль")

                if user.banned:
                    return DataFailedMessage("Пользователь заблокирован",code=423)

                #logger.info(f"Пользователь {user.user_name} успешно вошел в аккаунт")
                return DataSuccess(User.model_validate(user))
            except Exception as e:
                return DataFailedMessage(f"Ошибка при проверки авторизации пользователя",error=e)

    @staticmethod
    def change_password(user_id, old_pwd, new_pwd_hash) -> DataState[User]:
        Session = connection_db()
        if not Session:
            return DataFailedMessage("Database connection error")

        with Session() as session:
            try:
                user = session.get(UserModel,user_id)
                if not check_password_hash(user.password_hash,old_pwd):
                    return DataFailedMessage("Неверный пароль")

                user.password_hash = new_pwd_hash
                session.commit()
                logger.debug(f"Пользователь {user.user_name} успешно сменил пароль")
                return DataSuccess(user)
            except Exception as e:
                session.rollback()
                return DataFailedMessage(f"Ошибка при проверки авторизации пользователя",error=e)

    @staticmethod
    def email_exists(email) -> DataState[User]:
        Session = connection_db()
        if not Session:
            return DataFailedMessage("Database connection error")

        with Session() as session:
            try:
                user = session.query(UserModel).filter(UserModel.email == email).first()
                return DataSuccess(user)

            except Exception as e:
                return DataFailedMessage(f"Ошибка при проверки почты", error=e)