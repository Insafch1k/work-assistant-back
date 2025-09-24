from project.models.ArticleModel import CreateArticleModel, UpdateArticleModel, ReadArticleModel
from project.utils.db_connection import DBConnection
from logger import Logger


class ArticlesDAL(DBConnection):
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
    def read_article(model: ReadArticleModel):
        """
        Возвращает boolean, dict\None

        Логика для BLL:
           1 - получаем True, result - значит данные есть и их можно конвертировать в json:
               json_data = json.dumps(result, ensure_ascii=False)
           2 - получаем False, None - возвращаем ответ о том, что данных нет
           3 - не получаем второй параметр: exception """

        article_id = model.id
        conn = ArticlesDAL.connect_db()

        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                stat = f"""SELECT author,
                                   header,
                                   description,
                                   category,
                                   created_at,
                                   updated_at,
                                   views
                                   FROM articles 
                                   WHERE id = %s"""
                cur.execute(stat, [article_id])
                result = cur.fetchone()
                if not result:
                    return False, None

                return True, result
        except Exception as e:
            Logger.error(f"ArticlesDal: Error when reading an article: {e}")
            conn.rollback()
            return False

    @staticmethod
    def update_article(model: UpdateArticleModel):
        conn = ArticlesDAL.connect_db()
        article_id = UpdateArticleModel.id
        try:
            fields_for_query = {k: v for k, v in model.dict(exclude_unset=True).items()}

            set_clause = ", ".join([f"{k}=%s" for k in fields_for_query.keys()])
            values = list(fields_for_query.values())
            values.append(article_id)

            stat = f"""UPDATE articles SET {set_clause} WHERE id = %s"""

            with conn.cursor() as cur:
                cur.execute(stat, values)
                conn.commit()

            return True
        except Exception as e:
            Logger.error(f"ArticlesDal: Error when updating an article: {e}")

            conn.rollback()
            return False

    @staticmethod
    def delete_article(model: DeleteArticleModel):
        article_id = DeleteArticleModel.id
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