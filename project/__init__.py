import redis
from flask import Flask, Blueprint
from flask_jwt_extended import JWTManager
from datetime import timedelta

from flask_mail import Mail
from loguru import logger

from project.config import settings, mail_config
from project.application.routes import all_routes

mail = Mail()

main_blueprint = Blueprint('main', __name__)
main_blueprint.register_blueprint(all_routes)


def create_app():
    app = Flask(__name__)
    app.config.from_object(mail_config)
    app.config["JWT_SECRET_KEY"] = settings.JWT_SECRET_KEY
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=settings.JWT_ACCESS_TOKEN_EXPIRES_HOURS)
    mail.init_app(app)
    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_is_revoked(jwt_header, jwt_payload: dict):
        redis_client = redis.Redis(db=1)
        jti = jwt_payload["jti"]
        key = f"blocked_tokens:{jti}"
        logger.debug(key)
        token_in_redis = redis_client.get(key)
        return token_in_redis is not None

    app.register_blueprint(main_blueprint)

    return app

