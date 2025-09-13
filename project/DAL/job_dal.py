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
    def add_job(employer_id, title, wanted_job, description, salary, date, time_start, time_end, address, city, is_urgent, xp, age, car):
        conn = JobDAL.connect_db()
        try:
            with conn.cursor() as cur:
                time_start_str = time_start if isinstance(time_start, str) else time_start.strftime('%H:%M')
                time_end_str = time_end if isinstance(time_end, str) else time_end.strftime('%H:%M')
                
                stat = """INSERT INTO jobs (
                                employer_id, title, wanted_job, description, salary,
                                date, time_start, time_end, address, city, is_urgent, xp, age, car, status
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, true)
                        RETURNING job_id, title, wanted_job, description, salary, date, time_start, time_end, created_at, 
                        address, city, car, is_urgent, xp, age"""
                cur.execute(stat, (
                    employer_id, title, wanted_job, description, salary, 
                    date, time_start_str, time_end_str, address, city, is_urgent, 
                    xp, age, car
                ))
                conn.commit()
                result = cur.fetchone()
                if not result:
                    Logger.error("Failed to create job - no data returned")
                    return None

                columns = [desc[0] for desc in cur.description]
                job_dict = dict(zip(columns, result))

                # Дополнительная обработка полей
                job_dict['time_start'] = str(job_dict['time_start']) if job_dict.get('time_start') else None
                job_dict['time_end'] = str(job_dict['time_end']) if job_dict.get('time_end') else None
                job_dict['created_at'] = job_dict['created_at'].isoformat() if job_dict.get('created_at') else None

                return job_dict

        except Exception as e:
            Logger.error(f"Error adding job: {str(e)}")
            conn.rollback()
            return None
        finally:
            conn.close()