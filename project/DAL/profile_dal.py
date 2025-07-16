from project.utils.db_connection import DBConnection
from project.utils.logger import Logger


class ProfileDAL(DBConnection):
    @staticmethod
    def get_user_role(user_id):
        conn = ProfileDAL.connect_db()
        try:
            with conn.cursor() as cur:
                stat = """SELECT user_role FROM users WHERE user_id = %s"""
                cur.execute(stat, (user_id,))
                conn.commit()
                return cur.fetchone()[0]
        except Exception as e:
            Logger.error(f"Error get user role {str(e)}")
            conn.rollback()
            return None
        finally:
            conn.close()

    @staticmethod
    def update_profile(user_id, user_name=None, phone=None, photo=None):
        conn = ProfileDAL.connect_db()
        try:
            with conn.cursor() as cur:
                if any([user_name, phone, photo]):
                    stat = """UPDATE users SET """

                    conditions = []
                    params = []

                    if user_name is not None:
                        conditions.append("user_name = %s")
                        params.append(user_name)

                    if phone:
                        conditions.append("phone = %s")
                        params.append(phone)

                    if photo:
                        conditions.append("photo = %s")
                        params.append(photo)

                    if conditions:
                        stat += ", ".join(conditions)

                    stat += " WHERE user_id = %s"
                    params.append(user_id)

                    cur.execute(stat, params)
                    conn.commit()
                    print(f"Данные пользователя успешно обновлены!")
        except Exception as e:
            Logger.error(f"Error update profile {str(e)}")
            conn.rollback()
        finally:
            conn.close()

    @staticmethod
    def update_employer_profile(organization_name, user_id):
        conn = ProfileDAL.connect_db()
        try:
            with conn.cursor() as cur:
                stat = """UPDATE employers SET organization_name = %s WHERE user_id = %s"""
                cur.execute(stat, (organization_name, user_id,))
                conn.commit()
                print(f"Данные работодателя успешно обновлены!")
        except Exception as e:
            Logger.error(f"Error update employer profile {str(e)}")
            conn.rollback()
        finally:
            conn.close()

    @staticmethod
    def update_finder_profile(age, user_id):
        conn = ProfileDAL.connect_db()
        try:
            with conn.cursor() as cur:
                stat = """UPDATE finders SET age = %s WHERE user_id = %s"""
                cur.execute(stat, (age, user_id,))
                conn.commit()
                print(f"Данные соискателя успешно обновлены!")
        except Exception as e:
            Logger.error(f"Error update finder profile {str(e)}")
            conn.rollback()
            return None
        finally:
            conn.close()

    @staticmethod
    def get_profile_data(profile_id):
        conn = ProfileDAL.connect_db()
        try:
            with conn.cursor() as cur:
                stat = """SELECT u.user_role, u.user_name, u.email, u.phone, u.photo, u.rating,
                                f.age, e.organization_name
                        FROM users u
                        LEFT JOIN finders f ON u.user_id = f.user_id
                        LEFT JOIN employers e ON u.user_id = e.user_id
                        WHERE u.user_id = %s"""
                cur.execute(stat, (profile_id,))
                return cur.fetchone()
        except Exception as e:
            Logger.error(f"Error get profile data {str(e)}")
            conn.rollback()
            return None
        finally:
            conn.close()

    @staticmethod
    def get_user_id_by_tg(tg):
        conn = ProfileDAL.connect_db()
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
    def get_employer_profile_data(employer_id):
        conn = ProfileDAL.connect_db()
        try:
            with conn.cursor() as cur:
                stat = """SELECT u.user_name, u.rating, u.tg_username, u.phone, u.photo, COUNT(r.review_id) as review_count
                          FROM users u
                          JOIN employers e ON u.user_id = e.user_id
                          LEFT JOIN reviews r ON r.employer_id = e.profile_id
                          WHERE e.profile_id = %s
                          GROUP BY u.user_id, e.profile_id"""
                cur.execute(stat, (employer_id,))
                conn.commit()
                return cur.fetchone()
        except Exception as e:
            Logger.error(f"Error get employer profile data {str(e)}")
            conn.rollback()
            return None
        finally:
            conn.close()


    @staticmethod
    def get_employer_jobs(employer_id):
        conn = ProfileDAL.connect_db()
        try:
            with conn.cursor() as cur:
                stat = """SELECT job_id, title, salary, address
                          FROM jobs
                          WHERE employer_id = %s AND status = true
                          ORDER BY created_at DESC"""
                cur.execute(stat, (employer_id,))
                conn.commit()
                result = cur.fetchall()
                return result
        except Exception as e:
            Logger.error(f"Error get employer jobs {str(e)}")
            conn.rollback()
            return None
        finally:
            conn.close()


    @staticmethod
    def check_finder(current_user_tg):
        conn = ProfileDAL.connect_db()
        try:
            with conn.cursor() as cur:
                stat = """SELECT u.user_id, f.profile_id
                          FROM users u
                          JOIN finders f ON u.user_id = f.user_id
                          WHERE u.tg = %s"""
                cur.execute(stat, (current_user_tg,))
                conn.commit()
                return cur.fetchone()
        except Exception as e:
            Logger.error(f"Error check finder {str(e)}")
            conn.rollback()
            return None
        finally:
            conn.close()


    @staticmethod
    def check_employer_exist(employer_id):
        conn = ProfileDAL.connect_db()
        try:
            with conn.cursor() as cur:
                stat = """SELECT 1 FROM employers WHERE profile_id = %s"""
                cur.execute(stat, (employer_id,))
                conn.commit()
                return cur.fetchone()
        except Exception as e:
            Logger.error(f"Error check employer exist {str(e)}")
            conn.rollback()
            return None
        finally:
            conn.close()


    @staticmethod
    def check_review(employer_id, user_id):
        conn = ProfileDAL.connect_db()
        try:
            with conn.cursor() as cur:
                stat = """SELECT review_id FROM reviews 
                          WHERE employer_id = %s AND reviewer_id = %s"""
                cur.execute(stat, (employer_id, user_id,))
                conn.commit()
                return cur.fetchone()
        except Exception as e:
            Logger.error(f"Error check review {str(e)}")
            conn.rollback()
            return None
        finally:
            conn.close()

    @staticmethod
    def add_review(employer_id, user_id, rating, comment):
        conn = ProfileDAL.connect_db()
        try:
            with conn.cursor() as cur:
                stat = """INSERT INTO reviews (employer_id, reviewer_id, rating, comment)
                          VALUES (%s, %s, %s, %s)
                          RETURNING review_id, created_at, updated_at"""
                cur.execute(stat, (employer_id, user_id, rating, comment,))
                conn.commit()
                return cur.fetchone()
        except Exception as e:
            Logger.error(f"Error add review {str(e)}")
            conn.rollback()
            return None
        finally:
            conn.close()


    @staticmethod
    def update_review(rating, comment, review_id):
        conn = ProfileDAL.connect_db()
        try:
            with conn.cursor() as cur:
                stat = """UPDATE reviews 
                          SET rating = %s, comment = %s, updated_at = NOW()
                          WHERE review_id = %s
                          RETURNING review_id, created_at, updated_at"""
                cur.execute(stat, (rating, comment, review_id,))
                conn.commit()
                return cur.fetchone()
        except Exception as e:
            Logger.error(f"Error update review {str(e)}")
            conn.rollback()
            return None
        finally:
            conn.close()


    @staticmethod
    def update_rating(employer_id):
        conn = ProfileDAL.connect_db()
        try:
            with conn.cursor() as cur:
                stat = """UPDATE users u
                          SET rating = (SELECT AVG(rating) 
                                        FROM reviews r
                                        JOIN employers e ON r.employer_id = e.profile_id
                                        WHERE e.user_id = u.user_id)
                          FROM employers e
                          WHERE u.user_id = e.user_id AND e.profile_id = %s"""
                cur.execute(stat, (employer_id,))
                conn.commit()
        except Exception as e:
            Logger.error(f"Error update rating {str(e)}")
            conn.rollback()
            return None
        finally:
            conn.close()