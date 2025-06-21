from project.utils.db_connection import DBConnection
from psycopg2 import Error


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
        except Error as e:
            print(f"Ошибка при получении id пользователя: {e}")
            conn.rollback()
        finally:
            conn.close()

    @staticmethod
    def create_resume(user_id, job_title, education, work_xp, skills):
        conn = ResumeDAL.connect_db()
        try:
            with conn.cursor() as cur:
                stat = """INSERT INTO resumes (user_id, job_title, education, work_xp, skills) 
                VALUES (%s, %s, %s, %s, %s)
                RETURNING resume_id, user_id, job_title, education, work_xp, skills"""
                cur.execute(stat, (user_id, job_title, education, work_xp, skills))
                conn.commit()
                print(f"Резюме пользователя успешно добавлено!")
                return cur.fetchone()
        except Error as e:
            print(f"Ошибка при создании резюме пользователя: {e}")
            conn.rollback()
        finally:
            conn.close()

    @staticmethod
    def check_resume(resume_id, current_user_tg):
        conn = ResumeDAL.connect_db()
        try:
            with conn.cursor() as cur:
                stat = """SELECT r.resume_id 
                            FROM resumes r
                            JOIN users u ON r.user_id = u.user_id
                            WHERE r.resume_id = %s AND u.tg = %s"""
                cur.execute(stat, (resume_id, current_user_tg,))
                conn.commit()
                return cur.fetchone()
        except Error as e:
            print(f"Ошибка при проверке существования резюме: {e}")
            conn.rollback()
        finally:
            conn.close()

    @staticmethod
    def delete_resume(resume_id):
        conn = ResumeDAL.connect_db()
        try:
            with conn.cursor() as cur:
                stat = """DELETE FROM resumes WHERE resume_id = %s"""
                cur.execute(stat, (resume_id,))
                conn.commit()
                print(f"Резюме пользователя успешно удалено!")
                return cur.fetchone()
        except Error as e:
            print(f"Ошибка при удалении резюме пользователя: {e}")
            conn.rollback()
        finally:
            conn.close()

    @staticmethod
    def get_resume_data(current_user_tg):
        conn = ResumeDAL.connect_db()
        try:
            with conn.cursor() as cur:
                stat = """SELECT r.resume_id, r.user_id, r.job_title, r.education, r.work_xp, r.skills
                          FROM resumes r
                          JOIN users u ON r.user_id = u.user_id
                          WHERE u.tg = %s"""
                cur.execute(stat, (current_user_tg,))
                conn.commit()
                return cur.fetchone()
        except Error as e:
            print(f"Ошибка при получении резюме пользователя: {e}")
            conn.rollback()
        finally:
            conn.close()
