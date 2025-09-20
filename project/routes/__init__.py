from flask import Blueprint

from project.routes.admin_route import admin_router
from project.utils.auto_delete_jobs import AutoDeleter

from project.routes.auth_route import auth_router
from project.routes.metrics_route import metrics_router
from project.routes.profile_route import profile_router, employer_profile_router
from project.routes.resume_route import resume_router
from project.routes.favorite_route import favorite_router
from project.routes.job_route import (job_router, filter_router, employer_jobs_router, finder_jobs_router,
                                      jobs_see_All_route, history_router)

all_routes = Blueprint("all_routes", __name__, url_prefix="/api")

ROUTERS_CLEAN_LIST = [
    job_router,
    filter_router,
    jobs_see_All_route,
    history_router,
    employer_jobs_router,
    employer_profile_router,
    finder_jobs_router
]

all_routes.register_blueprint(admin_router)
all_routes.register_blueprint(metrics_router)
all_routes.register_blueprint(auth_router)
all_routes.register_blueprint(profile_router)
all_routes.register_blueprint(resume_router)
all_routes.register_blueprint(favorite_router)

for router in ROUTERS_CLEAN_LIST:
    all_routes.register_blueprint(router)
    router.before_request(AutoDeleter.delete_expired_jobs)