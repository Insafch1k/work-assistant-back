from project.utils.db_connection import DBConnection
from project.utils.logger import Logger


class ResumeDAL(DBConnection):
    @staticmethod
    def get_user_id_by_tg(tg):
        conn = ResumeDAL.connect_db()
        try:
            with conn.cursor() as cur:
                stat = """SELECT user_id FROM users WHERE tg = %s"""
                cur.execute(stat, (tg,))
                conn.commit()
                return cur.fetchone()[0]
        except Exception as e:
            Logger.error(f"Error get user_id by tg {str(e)}")
            conn.rollback()
            return None
        finally:
            conn.close()

    @staticmethod
    def get_finder_id_by_tg(tg):
        conn = ResumeDAL.connect_db()
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
    def create_resume(user_id, job_title, education, work_xp, skills):
        conn = ResumeDAL.connect_db()
        try:
            with conn.cursor() as cur:
                stat = """INSERT INTO resume (user_id, job_title, education, work_xp, skills) 
                VALUES (%s, %s, %s, %s, %s)
                RETURNING resume_id, user_id, job_title, education, work_xp, skills"""
                cur.execute(stat, (user_id, job_title, education, work_xp, skills))
                conn.commit()
                print(f"Резюме пользователя успешно добавлено!")
                return cur.fetchone()
        except Exception as e:
            Logger.error(f"Error create resume {str(e)}")
            conn.rollback()
            return None
        finally:
            conn.close()

    @staticmethod
    def get_resume_id_by_finder(profile_id):
        conn = ResumeDAL.connect_db()
        try:
            with conn.cursor() as cur:
                stat = """SELECT r.resume_id 
                            FROM resume r
                            JOIN finders f ON r.user_id = f.user_id
                            WHERE f.profile_id = %s"""
                cur.execute(stat, (profile_id,))
                conn.commit()
                return cur.fetchone()
        except Exception as e:
            Logger.error(f"Error get resume_id by finder {str(e)}")
            conn.rollback()
            return None
        finally:
            conn.close()

    @staticmethod
    def delete_resume(resume_id):
        conn = ResumeDAL.connect_db()
        try:
            with conn.cursor() as cur:
                stat = """DELETE FROM resume WHERE resume_id = %s"""
                cur.execute(stat, (resume_id,))
                conn.commit()
                print(f"Резюме пользователя успешно удалено!")
                return cur.fetchone()
        except Exception as e:
            Logger.error(f"Error delete resume {str(e)}")
            conn.rollback()
            return None
        finally:
            conn.close()

    @staticmethod
    def update_resume(resume_id, job_title=None, education=None, work_xp=None, skills=None):
        conn = ResumeDAL.connect_db()
        try:
            with conn.cursor() as cur:
                args = {"job_title": job_title, "education": education, "work_xp": work_xp}

                if any(list(args.values())) or skills is not None:
                    stat = """UPDATE resume SET """
                    conditions = []
                    cur_params = []

                    for field, value in args.items():
                        if value is not None:
                            print(field, value)
                            conditions.append(f"{field} = %s")
                            cur_params.append(value)

                    if skills is not None:
                        conditions.append("skills = %s")
                        cur_params.append(','.join(skills))

                    if conditions:
                        stat += ", ".join(conditions)

                    stat += " WHERE resume_id = %s RETURNING resume_id, job_title, education, work_xp, skills"
                    cur_params.append(resume_id)

                    cur.execute(stat, cur_params)
                    conn.commit()
                    return cur.fetchone()
        except Exception as e:
            Logger.error(f"Error update resume {str(e)}")
            conn.rollback()
            return None
        finally:
            conn.close()

    @staticmethod
    def get_resume_data(current_user_tg):
        conn = ResumeDAL.connect_db()
        try:
            with conn.cursor() as cur:
                stat = """SELECT r.job_title, r.education, r.work_xp, r.skills
                          FROM resume r
                          JOIN users u ON r.user_id = u.user_id
                          WHERE u.tg = %s"""
                cur.execute(stat, (current_user_tg,))
                conn.commit()
                return cur.fetchone()
        except Exception as e:
            Logger.error(f"Error get resume data {str(e)}")
            conn.rollback()
            return None
        finally:
            conn.close()
