import psycopg2
from psycopg2.extras import RealDictCursor

from project.models.ArticleModel import CreateArticleModel, UpdateArticleModel, ReadArticleModel, DeleteArticleModel
from project.utils.db_connection import DBConnection
from project.utils.logger import Logger

class ArticlesDAL(DBConnection):

    @staticmethod
    def create_article( model: CreateArticleModel):
        conn = DBConnection.connect_db()

        try:
            with conn.cursor() as cursor:
                model_dict = model.dict(exclude_none=True)

                columns = ", ".join(model_dict.keys())
                placeholders = ", ".join(["%s"] * len(model_dict))
                values = tuple(model_dict.values())

                stat = f"INSERT INTO articles ({columns}) VALUES ({placeholders})"
                cursor.execute(stat, values)

                conn.commit()
                return True
        except Exception as e:
            conn.rollback()
            Logger.error(f"ArticlesDal: Error when adding an article to the database: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def read_article(article_id):
        conn = ArticlesDAL.connect_db()

        try:
            with conn.cursor(cursor_factory= RealDictCursor) as cur:
                stat = f"""SELECT * FROM articles WHERE id = %s"""
                cur.execute(stat, [article_id])
                result = cur.fetchone()
                if not result:
                    return False, None

                return result
        except Exception as e:
            Logger.error(f"ArticlesDal: Error when reading an article: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()

    @staticmethod
    def update_article( model: UpdateArticleModel):
        conn = DBConnection.connect_db()
        article_id = model.id

        try:
            fields_for_query = {k: v for k, v in model.dict(exclude_unset=True).items()}

            set_clause = ", ".join([f"{k}=%s" for k in fields_for_query.keys()])
            values = list(fields_for_query.values())
            values.append(article_id)

            stat = f"""UPDATE articles SET {set_clause} WHERE id = %s"""

            with conn.cursor() as cur:
                cur.execute(stat, values)
                conn.commit()
                return cur.rowcount
        except psycopg2.DatabaseError as e:
            Logger.error(f"ArticlesDal: Error when updating an article: {e}")
            conn.rollback()
            return None
        except psycopg2.Error as e:
            Logger.error(f"ArticlesDal: Database error in update article: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()

    @staticmethod
    def delete_article(model: DeleteArticleModel):
        article_id = model.id
        conn = ArticlesDAL.connect_db()
        try:
            with conn.cursor() as cur:
                stat = f"""DELETE FROM articles WHERE id = %s"""
                cur.execute(stat, [article_id])

                conn.commit()
                return True
        except Exception as e:
            Logger.error(f"ArticlesDal: Error when deleting an article: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    @staticmethod
    def get_similar_articles(category: str):
        conn = ArticlesDAL.connect_db()
        try:
            with conn.cursor(cursor_factory= RealDictCursor) as cur:
                stat = "SELECT * FROM articles WHERE category = %s LIMIT 10"
                cur.execute(stat, [category])

                row = cur.fetchone()
                if not row:
                    return False, None

                return True, row
        except Exception as e:
            Logger.error(f"ArticlesDal: Error when getting similar articles: {e}")
            return False
        finally:
            conn.close()
