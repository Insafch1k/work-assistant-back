from project.utils.db_connection import DBConnection
from project.utils.logger import Logger

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
        except Exception as e:
            Logger.error(f"Error get finder_id by tg {str(e)}")
            conn.rollback()
            return False
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
        except Exception as e:
            Logger.error(f"Error add job view {str(e)}")
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
                    SELECT 
                        j.job_id, 
                        j.employer_id, 
                        j.title, 
                        j.salary, 
                        j.address, 
                        j.time_start, 
                        j.time_end,
                        EXISTS (
                            SELECT 1 FROM job_favorites f 
                            WHERE f.job_id = j.job_id 
                            AND f.finder_id = %s
                        ) AS is_favorite, 
                        j.is_urgent, 
                        j.created_at, 
                        u.photo, 
                        u.rating,
                        j.car
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
        except Exception as e:
            Logger.error(f"Error get view history {str(e)}")
            conn.rollback()
            return []
        finally:
            conn.close()