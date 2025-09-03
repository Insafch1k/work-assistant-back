from project.utils.db_connection import DBConnection
from psycopg2 import Error
class ProfileDAL(DBConnection):
    @staticmethod
    def get_user_role(user_id):
        conn = ProfileDAL.connect_db()
        try:
            with conn.cursor() as cur:
                stat = """SELECT user_role FROM users WHERE user_id = %s"""
                cur.execute(stat, (user_id,))
                conn.commit()
                return cur.fetchone()[0]
        except Error as e:
            print(f"Ошибка при получении роли пользователя: {e}")
            conn.rollback()
        finally:
            conn.close()


    @staticmethod
    def update_profile(user_name, email, phone, photo, user_id):
        conn = ProfileDAL.connect_db()
        try:
            with conn.cursor() as cur:
                stat = """UPDATE users SET user_name = %s, email = %s, phone = %s, photo = %s WHERE user_id = %s"""
                cur.execute(stat, (user_name, email, phone, photo, user_id,))
                conn.commit()
                print(f"Данные пользователя успешно обновлены!")
        except Error as e:
            print(f"Ошибка при обновлении данных пользователя: {e}")
            conn.rollback()
        finally:
            conn.close()


    @staticmethod
    def update_employer_profile(organization_name, user_id):
        conn = ProfileDAL.connect_db()
        try:
            with conn.cursor() as cur:
                stat = """UPDATE employers SET organization_name = %s WHERE user_id = %s"""
                cur.execute(stat, (organization_name, user_id,))
                conn.commit()
                print(f"Данные работодателя успешно обновлены!")
        except Error as e:
            print(f"Ошибка при обновлении данных работодателя: {e}")
            conn.rollback()
        finally:
            conn.close()


    @staticmethod
    def update_finder_profile(age, user_id):
        conn = ProfileDAL.connect_db()
        try:
            with conn.cursor() as cur:
                stat = """UPDATE finders SET age = %s WHERE user_id = %s"""
                cur.execute(stat, (age, user_id,))
                conn.commit()
                print(f"Данные соискателя успешно обновлены!")
        except Error as e:
            print(f"Ошибка при обновлении данных соискателя: {e}")
            conn.rollback()
        finally:
            conn.close()


    @staticmethod
    def get_profile_data(profile_id):
        conn = ProfileDAL.connect_db()
        try:
            with conn.cursor() as cur:
                stat = """SELECT u.user_role, u.user_name, u.email, u.phone, u.photo, u.rating,
                                f.age, e.organization_name
                        FROM users u
                        LEFT JOIN finders f ON u.user_id = f.user_id
                        LEFT JOIN employers e ON u.user_id = e.user_id
                        WHERE u.user_id = %s"""
                cur.execute(stat, (profile_id,))
                return cur.fetchone()
        except Error as e:
            print(f"Ошибка при получении данных профиля: {e}")
            conn.rollback()
        finally:
            conn.close()


    @staticmethod
    def get_user_id_by_tg(tg):
        conn = ProfileDAL.connect_db()
        try:
            with conn.cursor() as cur:
                stat = """SELECT user_id FROM users WHERE tg = %s"""
                cur.execute(stat, (tg,))
                conn.commit()
                return cur.fetchone()[0]
        except Error as e:
            print(f"Ошибка при получении id пользователя: {e}")
            conn.rollback()
        finally:
            conn.close()