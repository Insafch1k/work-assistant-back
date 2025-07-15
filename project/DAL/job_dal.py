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
            Logger.error(f"Error get employer_id by tg: {str(e)}")
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
                # Преобразуем время в строку перед вставкой в БД
                time_start_str = time_start if isinstance(time_start, str) else time_start.strftime('%H:%M')
                time_end_str = time_end if isinstance(time_end, str) else time_end.strftime('%H:%M')
                
                stat = """INSERT INTO jobs (
                                employer_id, title, wanted_job, description, salary,
                                date, time_start, time_end, address, is_urgent, xp, age, car, status
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, true)
                        RETURNING job_id, title, wanted_job, salary, time_start, time_end, created_at, address, car"""
                cur.execute(stat, (
                    employer_id, title, wanted_job, description, salary, 
                    date, time_start_str, time_end_str, address, is_urgent, 
                    xp, age, car
                ))
                conn.commit()
                result = cur.fetchone()
                if not result:
                    Logger.error("Failed to create job - no data returned")
                    return None
                return result
        except Exception as e:
            Logger.error(f"Error adding job: {str(e)}")
            conn.rollback()
            return None
        finally:
            conn.close()