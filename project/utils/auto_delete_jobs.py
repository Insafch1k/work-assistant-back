from datetime import datetime

from project.utils.db_connection import DBConnection
from project.utils.logger import Logger


class AutoDeleter(DBConnection):
    @staticmethod
    def delete_expired_jobs():
        """Удаляет просроченные объявления."""
        conn = AutoDeleter.connect_db()
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM jobs WHERE date < %s", (datetime.now(),))
                conn.commit()
                Logger.info("Удалены просроченные объявления")
        except Exception as e:
            Logger.error(f"Error auto delete jobs: {str(e)}")
            conn.rollback()
        finally:
            conn.close()