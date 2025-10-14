from flask import Blueprint
from project.application.routes.profile.profile_route import profile_router
from project.application.routes.authorization.auth_route import auth_router
all_routes = Blueprint("all_routes", __name__, url_prefix="/api")


all_routes.register_blueprint(profile_router)
all_routes.register_blueprint(auth_router)