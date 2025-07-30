from project.utils.db_connection import DBConnection
from project.utils.logger import Logger


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
        except Exception as e:
            Logger.error(f"Error get finder_id by tg {str(e)}")
            conn.rollback()
            return False
        finally:
            conn.close()

    @staticmethod
    def get_filtered_jobs(wanted_job=None, address=None, time_start=None, time_end=None,
                        date=None, salary=None, salary_to=None, is_urgent=None, 
                        xp=None, age=None, car=None, city=None, finder_id=None):
        conn = FilterDAL.connect_db()
        try:
            with conn.cursor() as cur:
                base_query = """
                    SELECT j.job_id, j.employer_id, j.title, j.salary, j.address, j.time_start, j.time_end,
                    EXISTS (
                            SELECT 1 FROM job_favorites f 
                            WHERE f.job_id = j.job_id 
                            AND f.finder_id = %s
                    ) AS is_favorite, j.is_urgent, j.created_at, u.photo, u.rating, j.car, u.phone, u.tg_username, j.city
                    FROM jobs j
                    JOIN employers e ON e.profile_id = j.employer_id
                    JOIN users u ON u.user_id = e.user_id
                    WHERE j.status = true
                """
                params = [finder_id] if finder_id else [None]

                conditions = []

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

                if salary_to is not None:
                    conditions.append("j.salary <= %s")
                    params.append(salary_to)

                if is_urgent is not None:
                    conditions.append("j.is_urgent = %s")
                    params.append(is_urgent)

                if xp is not None:
                    conditions.append("j.xp = %s")
                    params.append(xp)

                if age is not None:
                    if age == "старше 18 лет":
                        conditions.append("j.age = 'старше 18 лет'")
                    elif age == "старше 16 лет":
                        conditions.append("(j.age = 'старше 16 лет' OR j.age = 'старше 18 лет')")
                    elif age == "старше 14 лет":
                        conditions.append("(j.age = 'старше 14 лет' OR j.age = 'старше 16 лет' OR j.age = 'старше 18 лет')")

                if car is not None:
                    conditions.append("j.car = %s")
                    params.append(car)

                if city is not None:
                    conditions.append("j.city ILIKE %s")
                    params.append(f"%{city}%")

                if conditions:
                    base_query += " AND " + " AND ".join(conditions)

                base_query += " ORDER BY j.created_at DESC"

                cur.execute(base_query, params)
                return cur.fetchall()
        except Exception as e:
            Logger.error(f"Error get filtered jobs {str(e)}")
            conn.rollback()
            return False
        finally:
            conn.close()