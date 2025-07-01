from project.utils.db_connection import DBConnection
from psycopg2 import Error

class Jobs(DBConnection):
    @staticmethod
    def get_finder_id_by_tg(tg):
        conn = Jobs.connect_db()
        try:
            with conn.cursor() as cur:
                stat = """SELECT f.profile_id 
                          FROM finders f
                          JOIN users u ON f.user_id = u.user_id
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
    def get_job_seeAll(job_id):
        conn = Jobs.connect_db()
        try:
            with conn.cursor() as cur:
                stat = """
                    SELECT j.title, j.salary, j.address, j.time_start, j.time_end, j.is_urgent, j.xp, j.age
                    FROM jobs j
                    WHERE j.job_id = %s
                    """
                cur.execute(stat, (job_id, ))
                conn.commit()
                return cur.fetchall()
        except Error as e:
            print(f"Ошибка получения подробнее обьявления из БД {e}")
            return None
        finally:
            conn.close()