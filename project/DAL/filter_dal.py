from project.utils.db_connection import DBConnection
from psycopg2 import Error


class FilterDAL(DBConnection):
    @staticmethod
    def get_finder_id_by_tg(tg):
        conn = FilterDAL.connect_db()
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
        except Error as e:
            print(f"Ошибка при получении id соискателя: {e}")
            conn.rollback()
        finally:
            conn.close()

    @staticmethod
    def get_filtered_jobs(wanted_job=None, address=None, time_start=None, time_end=None,
                          date=None, salary=None, is_urgent=None, xp=None, age=None):
        conn = FilterDAL.connect_db()
        try:
            with conn.cursor() as cur:
                base_query = """
                    SELECT j.job_id, j.title, j.wanted_job, j.description, j.salary, j.date, j.time_start, j.time_end, 
                        j.address, j.is_urgent, e.organization_name, j.created_at
                    FROM jobs j
                    JOIN employers e ON j.employer_id = e.profile_id
                    WHERE j.status = true
                """

                conditions = []
                params = []

                if wanted_job is not None:
                    conditions.append("j.wanted_job ILIKE %s")
                    params.append(f"%{wanted_job}%")

                if address is not None:
                    conditions.append("j.address ILIKE %s")
                    params.append(f"%{address}%")

                if time_start is not None:
                    conditions.append("j.time_start >= %s")
                    params.append(time_start)

                if time_end is not None:
                    conditions.append("j.time_end <= %s")
                    params.append(time_end)

                if date is not None:
                    conditions.append("j.date::date = %s::date")
                    params.append(date)

                if salary is not None:
                    conditions.append("j.salary >= %s")
                    params.append(salary)

                if is_urgent is not None:
                    conditions.append("j.is_urgent = %s")
                    params.append(is_urgent)

                if xp is not None:
                    conditions.append("j.xp = %s")
                    params.append(xp)

                if age:
                    if age == "Старше 14 лет":
                        conditions.append("j.age >= 14 AND j.age = 'Старше 16 лет' AND j.age = 'Старше 18 лет'")
                    elif age == "Старше 16 лет":
                        conditions.append("j.age >= 16 AND j.age = 'Старше 18 лет'")
                    elif age == "Старше 18 лет":
                        conditions.append("j.age = %s")

                if conditions:
                    base_query += " AND " + " AND ".join(conditions)

                base_query += " ORDER BY j.created_at DESC"

                cur.execute(base_query, params)
                return cur.fetchall()
        except Error as e:
            print(f"Ошибка при фильтрации объявлений: {e}")
            conn.rollback()
        finally:
            conn.close()