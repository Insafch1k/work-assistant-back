from project.utils.db_connection import DBConnection
from psycopg2 import Error

class Emplyers_Jobs(DBConnection):
    @staticmethod
    def get_finder_id_by_tg(tg):
        conn = Emplyers_Jobs.connect_db()
        try:
            with conn.cursor() as cur:
                stat = """SELECT e.profile_id 
                          FROM employers e
                          JOIN users u ON e.user_id = u.user_id
                          WHERE u.tg = %s"""
                cur.execute(stat, (tg,))
                conn.commit()
                return cur.fetchone()[0]
        except Error as e:
            print(f"Ошибка при получении id соискателя: {e}")
            conn.rollback()
        finally:
            conn.close()

    @staticmethod
    def get_all_jobs(employer_id):
        conn = Emplyers_Jobs.connect_db()
        try:
            with conn.cursor() as cur:
                stat = """
                   SELECT j.job_id, j.employer_id, j.title, j.salary, j.address, j.time_start, j.time_end,
                   EXISTS (
                        SELECT 1 FROM job_favorites f 
                        WHERE f.job_id = j.job_id 
                        AND f.finder_id = %s
                   ) AS is_favorite, j.created_at
                   FROM jobs j
                   ORDER BY j.created_at"""
                cur.execute(stat, (employer_id, ))
                conn.commit()
                return cur.fetchall()
        except Error as e:
            print(f"Ошибка получения обьявлений из БД {e}")
            conn.rollback()
            return []
        finally:
            conn.close()

    
