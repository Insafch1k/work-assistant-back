from project.utils.db_connection import DBConnection
from project.utils.logger import Logger


class AuthDAL(DBConnection):
    @staticmethod
    def add_user(tg, user_role, user_name):
        conn = AuthDAL.connect_db()
        try:
            with conn.cursor() as cur:
                stat = """INSERT INTO users (tg, user_role, user_name, rating)
                          VALUES (%s, %s, %s, 0.0)
                          RETURNING user_id, tg, user_role, user_name, rating"""
                cur.execute(stat, (tg, user_role, user_name, ))
                conn.commit()
                print(f"Пользователь {user_name} успешно добавлен!")
                return cur.fetchone()
        except Exception as e:
            Logger.error(f"Error add user {str(e)}")
            conn.rollback()
            return False
        finally:
            conn.close()

    @staticmethod
    def add_finder(user_id):
        conn = AuthDAL.connect_db()
        try:
            with conn.cursor() as cur:
                stat = """INSERT INTO finders (user_id) VALUES (%s)"""
                cur.execute(stat, (user_id, ))
                conn.commit()
                print(f"Соискатель успешно добавлен!")
        except Exception as e:
            Logger.error(f"Error add finder {str(e)}")
            conn.rollback()
            return False
        finally:
            conn.close()

    @staticmethod
    def add_employer(user_id):
        conn = AuthDAL.connect_db()
        try:
            with conn.cursor() as cur:
                stat = """INSERT INTO employers (user_id) VALUES (%s)"""
                cur.execute(stat, (user_id, ))
                conn.commit()
                print(f"Работодатель успешно добавлен!")
        except Exception as e:
            Logger.error(f"Error add employer {str(e)}")
            conn.rollback()
            return False
        finally:
            conn.close()

    @staticmethod
    def check_user(tg):
        conn = AuthDAL.connect_db()
        try:
            with conn.cursor() as cur:
                stat = """SELECT EXISTS(SELECT user_id FROM users WHERE tg = %s)"""
                cur.execute(stat, (tg, ))
                return cur.fetchone()[0]
        except Exception as e:
            Logger.error(f"Error check user {str(e)}")
            conn.rollback()
            return False
        finally:
            conn.close()