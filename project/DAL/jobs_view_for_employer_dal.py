from project.utils.db_connection import DBConnection
from project.utils.logger import Logger

class Emplyers_Jobs(DBConnection):
    @staticmethod
    def get_employer_id_by_tg(tg):
        conn = Emplyers_Jobs.connect_db()
        try:
            with conn.cursor() as cur:
                stat = """SELECT e.profile_id 
                          FROM employers e
                          JOIN users u ON e.user_id = u.user_id
                          WHERE u.tg = %s"""
                cur.execute(stat, (tg,))
                conn.commit()
                return cur.fetchone()[0]
        except Exception as e:
            Logger.error(f"Error get employer_id by tg {str(e)}")
            conn.rollback()
            return None
        finally:
            conn.close()

    @staticmethod
    def get_all_jobs(employer_id, cities=None):
        conn = Emplyers_Jobs.connect_db()
        try:
            with conn.cursor() as cur:
                stat = """
                    SELECT j.job_id, j.employer_id, u.tg_username, u.phone, j.title, j.salary, j.address, j.time_start, j.time_end,
                    EXISTS (
                            SELECT 1 FROM job_favorites f 
                            WHERE f.job_id = j.job_id 
                            AND f.finder_id = %s
                    ) AS is_favorite, j.is_urgent, j.created_at, u.photo, u.rating, j.car, j.city
                    FROM jobs j
                    JOIN employers e ON e.profile_id = j.employer_id
                    JOIN users u ON u.user_id = e.user_id
                    WHERE j.status = true"""
                params = [employer_id]

                if cities:
                    stat += " AND j.city = ANY(%s)"
                    params.append(cities)

                stat += " ORDER BY j.created_at DESC"
                cur.execute(stat, params)
                conn.commit()
                return cur.fetchall()
        except Exception as e:
            Logger.error(f"Error get all jobs {str(e)}")
            conn.rollback()
            return []
        finally:
            conn.close()

    @staticmethod
    def get_my_employer_jobs(employer_id):
        conn = Emplyers_Jobs.connect_db()
        try:
            with conn.cursor() as cur:
                stat = """
                SELECT j.job_id, j.employer_id, j.title, j.salary, j.address, j.time_start, j.time_end,
                j.is_urgent, j.created_at, j.wanted_job, j.date, j.xp, j.age, j.description, j.car, j.city
                FROM jobs j
                JOIN employers e ON e.profile_id = j.employer_id
                JOIN users u ON u.user_id = e.user_id
                WHERE j.employer_id = %s
                ORDER BY j.created_at DESC"""
                cur.execute(stat, (employer_id,))
                conn.commit()
                return cur.fetchall()
        except Exception as e:
            Logger.error(f"Error get my employer jobs {str(e)}")
            conn.rollback()
            return None
        finally:
            conn.close()

    @staticmethod
    def update_my_employer_job(job_id, title=None, wanted_job=None, description=None, salary=None, date=None,
                            time_start=None, time_end=None, address=None, is_urgent=None,
                            xp=None, age=None, status=None, car=None, city=None):
        conn = Emplyers_Jobs.connect_db()
        try:
            with conn.cursor() as cur:
                args = {
                    "title": title, 
                    "wanted_job": wanted_job, 
                    "description": description, 
                    "salary": salary,
                    "date": date, 
                    "time_start": time_start, 
                    "time_end": time_end, 
                    "address": address,
                    "xp": xp, 
                    "age": age, 
                    "status": status,
                    "city": city
                }
                
                if any(value is not None for value in args.values()):
                    stat = """UPDATE jobs SET """
                    updates = []
                    params = []

                    if is_urgent is not None or isinstance(is_urgent, bool):
                        updates.append("is_urgent = %s")
                        params.append(is_urgent)

                    if car is not None or isinstance(car, bool):
                        updates.append("car = %s")
                        params.append(car)

                    for field, value in args.items():
                        if value is not None:
                            updates.append(f"{field} = %s")
                            params.append(value)

                    if updates:
                        stat += ", ".join(updates)
                        stat += " WHERE job_id = %s"
                        params.append(job_id)

                        cur.execute(stat, params)
                        conn.commit()
                        return True
                return False
        except Exception as e:
            Logger.error(f"Error update my employer job: {str(e)}")
            conn.rollback()
            return None
        finally:
            conn.close()
    
    @staticmethod
    def delete_my_employer_job(job_id, employer_id):
        conn = Emplyers_Jobs.connect_db()
        try:
            with conn.cursor() as cur:
                # Проверяем, что вакансия принадлежит работодателю
                check_stat = """SELECT 1 FROM jobs WHERE job_id = %s AND employer_id = %s"""
                cur.execute(check_stat, (job_id, employer_id))
                if not cur.fetchone():
                    Logger.error(f"Job {job_id} not found or not owned by employer {employer_id}")
                    return False

                # Удаляем связанные записи из job_favorites
                delete_favorites_stat = """DELETE FROM job_favorites WHERE job_id = %s"""
                cur.execute(delete_favorites_stat, (job_id,))

                # Полностью удаляем вакансию из jobs
                delete_job_stat = """DELETE FROM jobs WHERE job_id = %s"""
                cur.execute(delete_job_stat, (job_id,))

                conn.commit()
                return True
        except Exception as e:
            Logger.error(f"Error deleting job {job_id}: {str(e)}")
            conn.rollback()
            return False
        finally:
            conn.close()