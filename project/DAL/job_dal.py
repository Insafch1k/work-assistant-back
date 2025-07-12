from project.utils.db_connection import DBConnection
from project.utils.logger import Logger


class JobDAL(DBConnection):
    @staticmethod
    def get_employer_id_by_tg(tg):
        conn = JobDAL.connect_db()
        try:
            with conn.cursor() as cur:
                stat = """SELECT e.profile_id 
                          FROM employers e
                          JOIN users u ON e.user_id = u.user_id
                          WHERE u.tg = %s"""
                cur.execute(stat, (tg,))
                conn.commit()
                result = cur.fetchone()
                return result[0] if result else None
        except Exception as e:
            Logger.error(f"Error get employer_id by tg {str(e)}")
            conn.rollback()
            return None
        finally:
            conn.close()

    @staticmethod
    def add_job(employer_id, title, wanted_job, description, salary, date, time_start, time_end, address,
                is_urgent, xp, age, car):
        conn = JobDAL.connect_db()
        try:
            with conn.cursor() as cur:
                stat = """INSERT INTO jobs (
                                employer_id, title, wanted_job, description, salary,
                                date, time_start, time_end, address, is_urgent, xp, age, car, status
                          )
                          VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, true)
                          RETURNING job_id, title, wanted_job, salary, time_start, time_end, created_at, address, car"""
                cur.execute(stat, (employer_id, title, wanted_job, description, salary, date, time_start, time_end,
                                  address, is_urgent, xp, age, car))
                conn.commit()
                return cur.fetchone()
        except Exception as e:
            Logger.error(f"Error add job {str(e)}")
            conn.rollback()
            return None
        finally:
            conn.close()