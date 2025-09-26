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
                    j.xp, j.age, j.description, j.car, j.city,
                    EXISTS (
                        SELECT 1 FROM job_favorites f 
                        WHERE f.job_id = j.job_id 
                        AND f.finder_id = %s
                    ) AS is_favorite,
                    j.wanted_job,
                    u.user_name,
                    u.phone,
                    u.tg_username
                    FROM jobs j
                    JOIN employers e ON e.profile_id = j.employer_id
                    JOIN users u ON u.user_id = e.user_id
                    WHERE j.job_id = %s
                    """
                cur.execute(stat, (finder_id, job_id,))
                result = cur.fetchone()
                columns = [desc[0] for desc in cur.description]
                job_dict = dict(zip(columns, result))

                job_dict['time_start'] = job_dict['time_start'].isoformat() if job_dict.get('time_start') else None
                job_dict['time_end'] = job_dict['time_end'].isoformat() if job_dict.get('time_end') else None
                job_dict['date'] = job_dict['date'].isoformat() if job_dict.get('date') else None

                return job_dict
        except Exception as e:
            Logger.error(f"Error get job seeAll {str(e)}")
            conn.rollback()
            return None
        finally:
            conn.close()