from project.utils.db_connection import DBConnection
from psycopg2 import Error

class HistoryDAL(DBConnection):
    @staticmethod
    def get_finder_id_by_tg(tg):
        conn = HistoryDAL.connect_db()
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
    def add_job_view(finder_id, job_id):
        conn = HistoryDAL.connect_db()
        try:
            with conn.cursor() as cur:
                stat = """INSERT INTO job_view_history (finder_id, job_id) VALUES (%s, %s)
                ON CONFLICT (finder_id, job_id) DO NOTHING
                RETURNING history_id, finder_id, job_id, viewed_at"""
                cur.execute(stat, (finder_id, job_id))
                conn.commit()
                result = cur.fetchone()
                return result if result else None
        except Error as e:
            print(f"Ошибка при добавлении просмотра вакансии: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()

    @staticmethod
    def get_view_history(finder_id):
        conn = HistoryDAL.connect_db()
        try:
            with conn.cursor() as cur:
                stat = """
                    SELECT j.job_id, j.employer_id, j.title, j.salary, j.address, j.time_start, j.time_end,
                        EXISTS (
                            SELECT 1 FROM job_favorites f 
                            WHERE f.job_id = j.job_id 
                            AND f.finder_id = %s
                        ) AS is_favorite, j.is_urgent, j.created_at, u.photo, u.rating
                    FROM job_view_history h
                    JOIN jobs j ON h.job_id = j.job_id
                    JOIN employers e ON j.employer_id = e.profile_id
                    JOIN users u ON u.user_id = e.user_id
                    WHERE h.finder_id = %s AND j.status = true
                    ORDER BY h.viewed_at DESC
                    """
                cur.execute(stat, (finder_id, finder_id,))
                conn.commit()
                return cur.fetchall()
        except Error as e:
            print(f"Ошибка получения списка историй {e}")
            conn.rollback()
            return []
        finally:
            conn.close()
        
    @staticmethod
    def check_view_exsists(finder_id, job_id):
        conn = HistoryDAL.connect_db()
        try:
            with conn.cursor() as cur:
                stat = """
                    SELECT 1 FROM job_view_history
                    WHERE finder_id = %s AND job_id = %s                    
                    """
                cur.execute(stat, (finder_id, job_id))
                conn.commit()
                return cur.fetchone() is not None
        
        except Error as e:
            print("Ошибка при проверке просмотра {e}")
            conn.rollback()
            return False
        finally:
            conn.close()