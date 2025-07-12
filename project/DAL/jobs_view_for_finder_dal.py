from project.utils.db_connection import DBConnection
from project.utils.logger import Logger


class Finder_Jobs(DBConnection):
    @staticmethod
    def get_finder_id_by_tg(tg):
        conn = Finder_Jobs.connect_db()
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
    def get_all_jobs(finder_id):
        conn = Finder_Jobs.connect_db()
        try:
            with conn.cursor() as cur:
                stat = """SELECT j.job_id, j.employer_id, j.title, j.salary, j.address, j.time_start, j.time_end,
                   EXISTS (
                        SELECT 1 FROM job_favorites f 
                        WHERE f.job_id = j.job_id 
                        AND f.finder_id = %s
                   ) AS is_favorite, j.is_urgent, j.created_at, u.photo, u.rating, j.car
                   FROM jobs j
                   JOIN employers e ON e.profile_id = j.employer_id
                   JOIN users u ON u.user_id = e.user_id
                   ORDER BY j.created_at DESC"""
                cur.execute(stat, (finder_id,))
                conn.commit()
                return cur.fetchall()
        except Exception as e:
            Logger.error(f"Error get all jobs {str(e)}")
            conn.rollback()
            return []
        finally:
            conn.close()

    @staticmethod
    def get_job_seeAll(job_id):
        conn = Finder_Jobs.connect_db()
        try:
            with conn.cursor() as cur:
                stat = """
                    SELECT j.title, j.salary, j.address, j.time_start, j.time_end, j.is_urgent,
                    j.work_xp, j.age_restrict, j.car
                    FROM jobs j
                    WHERE j.job_id = %s
                    ORDER BY j.created_at DESC
                    """
                cur.execute(stat, (job_id,))
                conn.commit()
                return cur.fetchall()
        except Exception as e:
            Logger.error(f"Error get job seeAll {str(e)}")
            conn.rollback()
            return None
        finally:
            conn.close()