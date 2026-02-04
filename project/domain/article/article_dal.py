from slugify import slugify
from sqlalchemy import func
from project.application.entities.article import Article, ArticleBaseInfo
from project.application.entities.category import Category
from project.domain.core.models.article import ArticleModel
from project.domain.core.models.article_category import CategoryArticleModel
from project.domain.core.models.category import CategoryModel
from project.utils.data_state import DataSuccess, DataFailedMessage
from project.utils.db_connection import connection_db


class ArticleDal:
    @staticmethod
    def get_articles(limit, offset, category_id, sort, search):
        Session = connection_db()
        if not Session:
            return DataFailedMessage("Database connection error")

        with Session() as session:
            try:
                query = session.query(ArticleModel)

                if search:
                    search_term = f"%{search.strip()}%"
                    query = query.filter(ArticleModel.h1.like(search_term))

                if category_id:
                    query.join(ArticleModel.categories).filter(CategoryModel.id == int(category_id))

                articles = query.order_by(ArticleModel.created_at.desc()).offset(offset).limit(limit).all()
                if sort == 1:
                    articles = list(reversed(articles))


                return DataSuccess(list(map(lambda article: ArticleBaseInfo.model_validate(article).model_dump(), articles)))
            except Exception as e:
                return DataFailedMessage(
                    "Ошибка при получении списка статей",
                    error=e,
                )

    @staticmethod
    def get_categories():
        Session = connection_db()
        if not Session:
            return DataFailedMessage("Database connection error")

        with Session() as session:
            try:
                categories = (
                    session.query(
                        CategoryModel.id,
                        CategoryModel.title,
                        CategoryModel.slug,
                        func.count(CategoryArticleModel.article_id).label('articles_count')
                    )
                    .outerjoin(CategoryArticleModel, CategoryModel.id == CategoryArticleModel.category_id)
                    .group_by(CategoryModel.id, CategoryModel.title, CategoryModel.slug)
                    .order_by(CategoryModel.title)
                ).all()

                return DataSuccess(list(map(lambda category: Category.model_validate(category).model_dump(), categories)))
            except Exception as e:
                return DataFailedMessage(
                    "Ошибка при получении списка категорий",
                    error=e,
                )

    @staticmethod
    def get_article_info(slug: str):
        Session = connection_db()
        if not Session:
            return DataFailedMessage("Database connection error")

        with Session() as session:
            try:
                article = session.query(ArticleModel).filter(ArticleModel.slug == slug).first()
                if not article:
                    return DataFailedMessage("Статья не найдена",code=404)

                category_ids = list(map(lambda cat: cat.category.id,article.categories))
                query = (session.query(ArticleModel)).join(ArticleModel.categories).filter(CategoryModel.id.in_(category_ids),
                    CategoryArticleModel.article_id != article.id)
                similar_articles = query.order_by(ArticleModel.created_at.desc()).limit(4).all()

                return DataSuccess({"article":Article.model_validate(article).model_dump(),
                                    "similar_articles": (list(map(lambda article: ArticleBaseInfo.model_validate(article).model_dump(), similar_articles)))})
            except Exception as e:
                return DataFailedMessage(
                    "Ошибка при получении статьи",
                    error=e,
                )

    @staticmethod
    def create_article(h1: str,
    image_url: str,
    description: str,
    seo_title: str,
    content: str,
    category_ids:list[int]):
        Session = connection_db()
        if not Session:
            return DataFailedMessage("Database connection error")

        with Session() as session:
            try:
                slug = slugify(h1)
                article = ArticleModel(h1=h1,image_url=image_url,description=description,content=content,slug=slug,seo_title=seo_title)
                session.add(article)
                session.flush()

                for cat_id in category_ids:
                    cat = CategoryArticleModel(article_id=article.id,category_id=cat_id)
                    session.add(cat)

                session.commit()
                return DataSuccess("Статья создана")
            except Exception as e:
                session.rollback()
                return DataFailedMessage(
                    "Ошибка при создании статьи",
                    error=e,
                )

    @staticmethod
    def create_category(title: str):
        Session = connection_db()
        if not Session:
            return DataFailedMessage("Database connection error")

        with Session() as session:
            try:
                slug = slugify(title)
                category = CategoryModel(title=title,slug=slug)
                session.add(category)
                session.commit()

                return DataSuccess("Категория создана")
            except Exception as e:
                session.rollback()
                return DataFailedMessage(
                    "Ошибка при создании категории",
                    error=e,
                )