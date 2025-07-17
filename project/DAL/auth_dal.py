from project.utils.db_connection import DBConnection
from project.utils.logger import Logger


class AuthDAL(DBConnection):
    @staticmethod
    def add_user(tg, tg_username, user_role, user_name, photo):
        conn = AuthDAL.connect_db()
        try:
            with conn.cursor() as cur:
                stat = """INSERT INTO users (tg, tg_username, user_role, user_name, photo, rating)
                          VALUES (%s, %s, %s, %s, 0.0)
                          RETURNING user_id, tg, tg_username, user_role, user_name, rating"""
                cur.execute(stat, (tg, tg_username, user_role, user_name, ))
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

    @staticmethod
    def check_user_role(tg):
        conn = AuthDAL.connect_db()
        try:
            with conn.cursor() as cur:
                stat = """SELECT user_role FROM users WHERE tg = %s"""
                cur.execute(stat, (tg,))
                return cur.fetchone()[0]
        except Exception as e:
            Logger.error(f"Error check user {str(e)}")
            conn.rollback()
            return False
        finally:
            conn.close()

    @staticmethod
    def change_user_data(user_role, photo, tg_username, tg):
        conn = AuthDAL.connect_db()
        try:
            with conn.cursor() as cur:
                stat = """UPDATE users SET user_role = %s, photo = %s, tg_username = %s WHERE tg = %s 
                          RETURNING user_role, tg_username"""
                cur.execute(stat, (user_role, photo, tg_username, tg,))
                conn.commit()
                return cur.fetchone()[0]
        except Exception as e:
            Logger.error(f"Error check user {str(e)}")
            conn.rollback()
            return False
        finally:
            conn.close()