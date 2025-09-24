from project.models.ArticleModel import CreateArticleModel, UpdateArticleModel
from project.utils.db_connection import DBConnection
from logger import Logger


class ArticlesDAL(DBConnection):


### CRUD
    @staticmethod
    def create_article(model: CreateArticleModel):
        conn = ArticlesDAL.connect_db()
        try:
            with conn.cursor() as cursor:
                stat = """INSERT INTO articles (author, header, description, category) VALUES (%s, %s, %s, %s)"""
                cursor.execute(stat, model.author,
                               model.header,
                               model.description,
                               model.category)
                conn.commit()

                return True
        except Exception as e:
            conn.rollback()
            Logger.error(f"ArticlesDal: Error when adding an article to the database: {e}")
            return False
    @staticmethod
    def update_article(model: UpdateArticleModel):
        conn = ArticlesDAL.connect_db()
        article_id = UpdateArticleModel.id
        try:
            fields_for_query= {k: v for k, v in model.dict(exclude_unset=True).items()}

            set_clause = ", ".join([f"{k}=%s" for k in fields_for_query.keys()])
            values = list(fields_for_query.values())
            values.append(article_id)

            stat = f"UPDATE articles SET {set_clause} WHERE id = %s"

            with conn.cursor() as cur:
                cur.execute(stat, values)
                conn.commit()

            return True
        except Exception as e:
            Logger.error(f"ArticlesDal: Error when updating an article: {e}")

            conn.rollback()
            return False

