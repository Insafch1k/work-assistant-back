from project.utils.db_connection import DBConnection
from project.utils.logger import Logger

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
                result = cur.fetchone()
                return result[0] if result else None
        except Exception as e:
            Logger.error(f"Error get finder_id by tg {str(e)}")
            conn.rollback()
            return None
        finally:
            conn.close()

    @staticmethod
    def get_job_seeAll(finder_id, job_id):
        conn = Jobs.connect_db()
        try:
            with conn.cursor() as cur:
                stat = """
                    SELECT j.title, j.salary, j.address, j.date, j.time_start, j.time_end, j.is_urgent, 
                    j.xp, j.age, j.description,
                    EXISTS (
                        SELECT 1 FROM job_favorites f 
                        WHERE f.job_id = j.job_id 
                        AND f.finder_id = %s
                   ) AS is_favorite
                    FROM jobs j
                    WHERE j.job_id = %s
                    """
                cur.execute(stat, (finder_id, job_id, ))
                conn.commit()
                return cur.fetchall()
        except Exception as e:
            Logger.error(f"Error get job seeAll {str(e)}")
            conn.rollback()
            return None
        finally:
            conn.close()