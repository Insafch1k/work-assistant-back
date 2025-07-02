from project.utils.db_connection import DBConnection
from psycopg2 import Error

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
        except Error as e:
            print(f"Ошибка при получении id соискателя: {e}")
            conn.rollback()
        finally:
            conn.close()

    @staticmethod
    def get_all_jobs(employer_id):
        conn = Emplyers_Jobs.connect_db()
        try:
            with conn.cursor() as cur:
                stat = """
                   SELECT j.job_id, j.employer_id, j.title, j.salary, j.address, j.time_start, j.time_end,
                   EXISTS (
                        SELECT 1 FROM job_favorites f 
                        WHERE f.job_id = j.job_id 
                        AND f.finder_id = %s
                   ) AS is_favorite, j.is_urgent, j.created_at, u.photo, u.rating
                   FROM jobs j
                   JOIN employers e ON e.profile_id = j.employer_id
                   JOIN users u ON u.user_id = e.user_id
                   ORDER BY j.created_at DESC"""
                cur.execute(stat, (employer_id, ))
                conn.commit()
                return cur.fetchall()
        except Error as e:
            print(f"Ошибка получения обьявлений из БД {e}")
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
                   j.is_urgent, j.created_at
                   FROM jobs j
                   JOIN employers e ON e.profile_id = j.employer_id
                   JOIN users u ON u.user_id = e.user_id
                   WHERE j.employer_id = %s
                   ORDER BY j.created_at DESC"""
                cur.execute(stat, (employer_id,))
                conn.commit()
                return cur.fetchall()
        except Error as e:
            print(f"Ошибка получения подробнее обьявления из БД {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def update_my_employer_job(job_id, title=None, wanted_job=None, description=None, salary=None, date=None,
                               time_start=None, time_end=None, address=None, is_urgent=None,
                               xp=None, age=None, status=None):
        conn = Emplyers_Jobs.connect_db()
        try:
            with conn.cursor() as cur:
                args = {"title": title, "wanted_job": wanted_job, "description": description, "salary": salary,
                        "date": date, "time_start": time_start, "time_end": time_end, "address": address,
                        "xp": xp, "age": age, "status": status}
                if any(list(args.values())):
                    stat = """UPDATE jobs SET is_urgent = %s"""
                    conditions = []
                    cur_params = [is_urgent]

                    for field, value in args.items():
                        if value is not None:
                            print(field, value)
                            conditions.append(f"{field} = %s")
                            cur_params.append(value)

                    if conditions:
                        stat += ", " + ", ".join(conditions)

                    stat += " WHERE job_id = %s"
                    cur_params.append(job_id)

                    cur.execute(stat, cur_params)
                    conn.commit()
                    return True
        except Error as e:
            print(f"Ошибка получения подробнее обьявления из БД {e}")
            return None
        finally:
            conn.close()