from project.utils.db_connection import DBConnection
from psycopg2 import Error


class FavoriteDAL(DBConnection):
    @staticmethod
    def get_finder_id_by_tg(tg):
        conn = FavoriteDAL.connect_db()
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
    def check_job(job_id):
        conn = FavoriteDAL.connect_db()
        try:
            with conn.cursor() as cur:
                stat = """SELECT 1 FROM jobs WHERE job_id = %s"""
                cur.execute(stat, (job_id,))
                return cur.fetchone()
        except Error as e:
            print(f"Ошибка при проверке существования вакансии: {e}")
            conn.rollback()
        finally:
            conn.close()

    @staticmethod
    def get_status_job(job_id):
        conn = FavoriteDAL.connect_db()
        try:
            with conn.cursor() as cur:
                stat = """SELECT favorite_by FROM jobs WHERE job_id = %s"""
                cur.execute(stat, (job_id,))
                conn.commit()
                return cur.fetchone()[0]
        except Error as e:
            print(f"Ошибка при получении статуса вакансии: {e}")
            conn.rollback()
        finally:
            conn.close()

    @staticmethod
    def update_favorite_status(favorite_by, job_id):
        conn = FavoriteDAL.connect_db()
        try:
            with conn.cursor() as cur:
                stat = """UPDATE jobs 
                          SET favorite_by = %s 
                          WHERE job_id = %s
                          RETURNING job_id, title, favorite_by"""
                cur.execute(stat, (favorite_by, job_id,))
                conn.commit()
                return cur.fetchone()
        except Error as e:
            print(f"Ошибка при проверке существования вакансии: {e}")
            conn.rollback()
        finally:
            conn.close()

    @staticmethod
    def get_favorite_list(finder_id):
        conn = FavoriteDAL.connect_db()
        try:
            with conn.cursor() as cur:
                stat = """SELECT j.job_id, j.title, j.salary, j.address, j.time_start, j.time_end
                          FROM jobs j
                          JOIN employers e ON j.employer_id = e.profile_id
                          WHERE j.status = 'active' AND %s = ANY(j.favorite_by)
                          ORDER BY j.created_at DESC"""
                cur.execute(stat, (finder_id,))
                conn.commit()
                return cur.fetchall()
        except Error as e:
            print(f"Ошибка при проверке существования вакансии: {e}")
            print(f"Ошибка при получении id пользователя: {e}")
            conn.rollback()
        finally:
            conn.close()
