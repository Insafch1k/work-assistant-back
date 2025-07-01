from project.utils.db_connection import DBConnection
from psycopg2 import Error


class JobDAL(DBConnection):
    @staticmethod
    def get_employer_id_by_tg(tg):
        conn = JobDAL.connect_db()
        try:
            with conn.cursor() as cur:
                stat = """SELECT e.profile_id 
                          FROM employers e
                          JOIN users u ON e.user_id = u.user_id
                          WHERE u.tg = %s"""
                cur.execute(stat, (tg,))
                conn.commit()
                result = cur.fetchone()
                return result[0] if result else None
        except Error as e:
            print(f"Ошибка при получении id работодателя: {e}")
            conn.rollback()
        finally:
            conn.close()

    @staticmethod
    def add_job(employer_id, title, wanted_job, description, salary, date, time_start, time_end, address,
                is_urgent, xp, age):
        conn = JobDAL.connect_db()
        try:
            with conn.cursor() as cur:
                stat = """INSERT INTO jobs (
                                employer_id, title, wanted_job, description, salary,
                                date, time_start, time_end, address, is_urgent, xp, age, status
                          )
                          VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, true)
                          RETURNING job_id, title, wanted_job, salary, time_start, time_end, created_at, address"""
                cur.execute(stat, (employer_id, title, wanted_job, description, salary, date, time_start, time_end,
                                    address, is_urgent, xp, age,))
                conn.commit()
                return cur.fetchone()
        except Error as e:
            print(f"Ошибка при добавлении объявления: {e}")
            conn.rollback()
        finally:
            conn.close()
