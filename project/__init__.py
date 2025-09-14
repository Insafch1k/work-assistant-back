from flask import Flask, Blueprint
from flask_jwt_extended import JWTManager
from datetime import timedelta
from project.config import settings
from project.routes import all_routes

main_blueprint = Blueprint('main', __name__)
main_blueprint.register_blueprint(all_routes)


def create_app():
    app = Flask(__name__)
    app.config["JWT_SECRET_KEY"] = settings.JWT_SECRET_KEY
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=settings.JWT_ACCESS_TOKEN_EXPIRES_HOURS)

    jwt = JWTManager(app)

    app.register_blueprint(main_blueprint)

    return app