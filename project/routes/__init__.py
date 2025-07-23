from flask import Blueprint

from project.utils.auto_delete_jobs import AutoDeleter

from project.routes.auth_route import auth_router
from project.routes.profile_route import profile_router, employer_profile_router
from project.routes.resume_route import resume_router
from project.routes.favorite_route import favorite_router
from project.routes.job_route import (job_router, filter_router, employer_jobs_router, finder_jobs_router,
                                      jobs_see_All_route, history_router)

all_routes = Blueprint("all_routes", __name__, url_prefix="/api")

all_routes.register_blueprint(auth_router)
all_routes.register_blueprint(profile_router)
all_routes.register_blueprint(resume_router)
all_routes.register_blueprint(favorite_router)
all_routes.register_blueprint(filter_router)
all_routes.register_blueprint(job_router)
all_routes.register_blueprint(jobs_see_All_route)
all_routes.register_blueprint(history_router)
all_routes.register_blueprint(employer_jobs_router)
all_routes.register_blueprint(employer_profile_router)
all_routes.register_blueprint(finder_jobs_router)

@job_router.before_request
def run_cleanup():
    AutoDeleter.delete_expired_jobs()

@filter_router.before_request
def run_cleanup():
    AutoDeleter.delete_expired_jobs()

@jobs_see_All_route.before_request
def run_cleanup():
    AutoDeleter.delete_expired_jobs()

@history_router.before_request
def run_cleanup():
    AutoDeleter.delete_expired_jobs()

@employer_jobs_router.before_request
def run_cleanup():
    AutoDeleter.delete_expired_jobs()

@employer_profile_router.before_request
def run_cleanup():
    AutoDeleter.delete_expired_jobs()

@finder_jobs_router.before_request
def run_cleanup():
    AutoDeleter.delete_expired_jobs()