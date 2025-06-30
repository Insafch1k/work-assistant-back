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
                conn.commit()
                return cur.fetchone()
        except Error as e:
            print(f"Ошибка при проверке существования вакансии: {e}")
            conn.rollback()
        finally:
            conn.close()

    @staticmethod
    def get_status_job(finder_id, job_id):
        conn = FavoriteDAL.connect_db()
        try:
            with conn.cursor() as cur:
                stat = """INSERT INTO job_favorites (finder_id, job_id)
                          VALUES (%s, %s)
                          RETURNING favorite_id, finder_id, job_id, created_at"""
                cur.execute(stat, (finder_id, job_id,))
                conn.commit()
                return cur.fetchone()[0]
        except Error as e:
            print(f"Ошибка при получении статуса вакансии: {e}")
            conn.rollback()
        finally:
            conn.close()

    @staticmethod
    def delete_favorite_job(current_user_tg, favorite_id):
        conn = FavoriteDAL.connect_db()
        try:
            with conn.cursor() as cur:
                stat = """DELETE FROM job_favorites f
                          USING finders fi, users u
                          WHERE f.finder_id = fi.profile_id AND fi.user_id = u.user_id AND u.tg = %s 
                            AND f.favorite_id = %s
                          RETURNING f.favorite_id"""
                cur.execute(stat, (current_user_tg, favorite_id,))
                conn.commit()
                return cur.fetchone()[0]
        except Error as e:
            print(f"Ошибка при получении статуса вакансии: {e}")
            conn.rollback()
        finally:
            conn.close()


    @staticmethod
    def get_favorite_list(current_user_tg):
        conn = FavoriteDAL.connect_db()
        try:
            with conn.cursor() as cur:
                stat = """SELECT j.job_id, j.title, j.salary, j.address, j.date, j.time_start, j.time_end,
                            e.organization_name, f.favorite_id
                          FROM job_favorites f
                          JOIN jobs j ON f.job_id = j.job_id
                          JOIN employers e ON j.employer_id = e.profile_id
                          JOIN finders fi ON f.finder_id = fi.profile_id
                          JOIN users u ON fi.user_id = u.user_id
                          WHERE u.tg = %s
                          ORDER BY f.created_at DESC"""
                cur.execute(stat, (current_user_tg,))
                conn.commit()
                return cur.fetchone()[0]
        except Error as e:
            print(f"Ошибка при получении статуса вакансии: {e}")
            conn.rollback()
        finally:
            conn.close()