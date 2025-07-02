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
    def get_favorite_list(finder_id):
        conn = FavoriteDAL.connect_db()
        try:
            with conn.cursor() as cur:
                stat = """SELECT f.favorite_id, j.job_id, j.title, j.salary, j.time_start, j.time_end, 
                            j.address, u.rating, u.photo, 
                          FROM job_favorites f
                          JOIN jobs j ON f.job_id = j.job_id
                          JOIN employers e ON j.employer_id = e.profile_id
                          JOIN users u ON e.user_id = u.user_id
                          WHERE f.finder_id = %s AND j.status = true
                          ORDER BY j.created_at DESC"""
                cur.execute(stat, (finder_id,))
                conn.commit()
                return cur.fetchall()
        except Error as e:
            print(f"Ошибка при проверке существования вакансии: {e}")
            conn.rollback()
        finally:
            conn.close()

    @staticmethod
    def add_job_favorite(curr_id, job_id):
        conn = FavoriteDAL.connect_db()
        try:
            with conn.cursor() as cur:
                stat = """INSERT INTO job_favorites (finder_id, job_id)
                          VALUES (%s, %s)
                          ON CONFLICT (finder_id, job_id) DO NOTHING
                          RETURNING favorite_id, finder_id, job_id, created_at"""
                cur.execute(stat, (curr_id, job_id,))
                conn.commit()
                return cur.fetchone()
        except Error as e:
            print(f"Ошибка при проверке существования вакансии: {e}")
            conn.rollback()
        finally:
            conn.close()

    @staticmethod
    def delete_favorite_job(finder_id, job_id):
        conn = FavoriteDAL.connect_db()
        try:
            with conn.cursor() as cur:
                stat = """DELETE FROM job_favorites
                          WHERE finder_id = %s AND job_id = %s
                          RETURNING finder_id, job_id"""
                cur.execute(stat, (finder_id, job_id))
                conn.commit()
                return cur.fetchall()
        except Error as e:
            print(f"Ошибка при удалении из избранного: {e}")
            conn.rollback()
        finally:
            conn.close()
