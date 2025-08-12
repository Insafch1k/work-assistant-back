from project.utils.db_connection import DBConnection
from project.utils.logger import Logger
from datetime import datetime

class MetricsCollector(DBConnection):
    @staticmethod
    def collect_daily_metrics():
        """Собирает метрики за текущий день и записывает в таблицу daily_metrics"""
        try:
            conn = MetricsCollector.connect_db()
            with conn.cursor() as cur:
                # Определяем текущую дату
                today = datetime.now().date()

                # Подсчет новых пользователей за текущий день
                new_users_query = """
                    SELECT COUNT(*) 
                    FROM users 
                    WHERE DATE(created_at) = %s
                """
                cur.execute(new_users_query, (today,))
                new_users = cur.fetchone()[0]

                # Подсчет новых вакансий за текущий день
                new_jobs_query = """
                    SELECT COUNT(*) 
                    FROM jobs 
                    WHERE DATE(created_at) = %s AND status = true
                """
                cur.execute(new_jobs_query, (today,))
                new_jobs = cur.fetchone()[0]

                # Подсчет уникальных пользователей за текущий день
                unique_visitors_query = """
                    SELECT COUNT(DISTINCT user_id) 
                    FROM users 
                    WHERE DATE(last_login_at) = %s"""
                cur.execute(unique_visitors_query, (today,))
                unique_visitors = cur.fetchone()[0]

                # Проверяем, существует ли запись за текущий день
                check_query = """
                    SELECT 1 FROM daily_metrics WHERE metric_date = %s
                """
                cur.execute(check_query, (today,))
                exists = cur.fetchone()

                if exists:
                    # Обновляем существующую запись
                    update_query = """
                        UPDATE daily_metrics 
                        SET new_users = %s, new_jobs = %s, unique_visitors = %s
                        WHERE metric_date = %s
                    """
                    cur.execute(update_query, (new_users, new_jobs, unique_visitors, today))
                else:
                    # Создаем новую запись
                    insert_query = """
                        INSERT INTO daily_metrics (metric_date, new_users, new_jobs, unique_visitors)
                        VALUES (%s, %s, %s, %s)
                    """
                    cur.execute(insert_query, (today, new_users, new_jobs, unique_visitors))

                conn.commit()
                Logger.info(f"Metrics collected for {today}: {new_users} new users, {new_jobs} new jobs")
                return True
        except Exception as e:
            Logger.error(f"Error collecting daily metrics: {str(e)}")
            conn.rollback()
            return False
        finally:
            conn.close()