from flask import Blueprint
from project.application.routes.profile.profile_route import profile_router
from project.application.routes.admin.admin_route import admin_router
from project.application.routes.authorization.auth_route import auth_router
from project.application.routes.jobs.jobs_route import job_router
from project.application.routes.favorite.jobs_favorite_route import job_favorite_router
from project.application.routes.history.jobs_history_route import job_history_router
from project.application.routes.metrics.metric_route import mertic_router
all_routes = Blueprint("all_routes", __name__, url_prefix="/api")

all_routes.register_blueprint(admin_router)
all_routes.register_blueprint(profile_router)
all_routes.register_blueprint(auth_router)
all_routes.register_blueprint(job_router)
all_routes.register_blueprint(job_favorite_router)
all_routes.register_blueprint(job_history_router)
all_routes.register_blueprint(mertic_router)