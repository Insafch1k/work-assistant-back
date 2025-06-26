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
                return cur.fetchone()[0]
        except Error as e:
            print(f"Ошибка при получении id пользователя: {e}")
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
                    SELECT j.title, j.salary, (j.time_end - j.time_start), 
                           j.address, e.organization_name
                    FROM jobs j
                    JOIN employers e ON j.employer_id = e.profile_id
                    WHERE j.status = true
                """

                conditions = []
                params = []

                if wanted_job:
                    conditions.append("j.wanted_job ILIKE %s")
                    params.append(f"%{wanted_job}%")

                if address:
                    conditions.append("j.address ILIKE %s")
                    params.append(f"%{address}%")

                if time_start:
                    conditions.append("j.time_start >= %s")
                    params.append(time_start)

                if time_end:
                    conditions.append("j.time_end <= %s")
                    params.append(time_end)

                if date:
                    conditions.append("j.date::date = %s::date")
                    params.append(date)

                if salary is not None:
                    conditions.append("j.salary >= %s")
                    params.append(salary)

                if is_urgent is not None:
                    conditions.append("j.is_urgent = %s")
                    params.append(is_urgent)

                if xp is not None:
                    conditions.append("j.xp >= %s")
                    params.append(xp)

                if age:
                    if age == "Старше 14":
                        conditions.append("j.age >= 14")
                    elif age == "Старше 16":
                        conditions.append("j.age >= 16")
                    elif age == "Старше 18":
                        conditions.append("j.age >= 18")

                if conditions:
                    base_query += " AND " + " AND ".join(conditions)

                base_query += " ORDER BY j.created_at DESC"

                cur.execute(base_query, params)
                return cur.fetchall()
        except Error as e:
            print(f"Filter error: {e}")
            conn.rollback()
        finally:
            conn.close()