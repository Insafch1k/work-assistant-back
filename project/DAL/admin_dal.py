from typing import Optional

from psycopg2.extras import RealDictCursor

from project.utils.data_state import DataFailedMessage, DataSuccess, DataState
from project.utils.db_connection import DBConnection
from project.utils.logger import Logger


class AdminDAL(DBConnection):
    @staticmethod
    def get_users_by_name(offset: int = 0,
    limit: int = 20,
    name_filter: Optional[str] = None):
        conn = AdminDAL.connect_db()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                query = """SELECT * FROM users"""

                params = []
                # Добавляем фильтр по имени если указан
                if name_filter:
                    query += " WHERE user_name ILIKE %s"
                    params.append(f'%{name_filter}%')

                # Добавляем сортировку и пагинацию
                query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
                params.append(limit)
                params.append(offset)

                cur.execute(query, params)

                return DataSuccess(cur.fetchall())

        except Exception as e:
            Logger.error(f"Error get users {e}")
            return DataFailedMessage('')
        finally:
            conn.close()

    @staticmethod
    def ban_user(user_id: int) -> DataState:
        conn = AdminDAL.connect_db()
        try:
            with conn.cursor() as cur:
                    query = "UPDATE users SET banned = true WHERE user_id = %s"
                    cur.execute(query, (user_id,))
                    conn.commit()
                    return DataSuccess()

        except Exception as e:
            Logger.error(f"Ошибка при бане пользователя: {e}")
            conn.rollback()
            return DataFailedMessage("Ошибка при бане пользователя: {e}")
        finally:
            conn.close()

    @staticmethod
    def unban_user(user_id: int) -> DataState:
        conn = AdminDAL.connect_db()
        try:
            with conn.cursor() as cur:
                    query = "UPDATE users SET banned = false WHERE user_id = %s"
                    cur.execute(query, (user_id,))
                    conn.commit()
                    return DataSuccess()

        except Exception as e:
            Logger.error(f"Ошибка при разбане пользователя: {e}")
            conn.rollback()
            return DataFailedMessage()
        finally:
            conn.close()

    @staticmethod
    def is_admin(tg):
        conn = AdminDAL.connect_db()
        try:
            with conn.cursor() as cur:
                stat = """SELECT is_admin FROM users WHERE tg = %s"""
                cur.execute(stat, (tg,))
                return cur.fetchone()[0]
        except Exception as e:
            Logger.error(f"Error get is_admin by tg {str(e)}")
            return None
        finally:
            conn.close()