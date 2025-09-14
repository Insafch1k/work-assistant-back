from datetime import datetime, timedelta

from project.utils.db_connection import DBConnection
from project.utils.logger import Logger


class AutoDeleter(DBConnection):
    @staticmethod
    def delete_expired_jobs():
        """Удаляет просроченные объявления, созданные 5 дней назад."""
        conn = AutoDeleter.connect_db()
        try:
            with conn.cursor() as cur:
                five_days_ago = datetime.now() - timedelta(days=5)
                stat = """DELETE FROM jobs WHERE date < %s"""
                cur.execute(stat, (five_days_ago,))
                #deleted_count = cur.rowcount
                conn.commit()
                #if deleted_count > 0:
                #    Logger.info(f"Удалено {deleted_count} просроченных объявлений")
        except Exception as e:
            Logger.error(f"Error auto delete jobs: {str(e)}")
            conn.rollback()
        finally:
            conn.close()