from flask import Blueprint

from project.routes.auth_route import auth_router
from project.routes.profile_route import profile_router
from project.routes.resume_route import resume_router
from project.routes.favorite_route import favorite_router
from project.routes.job_route import job_router, filter_router, employer_jobs_router, finder_jobs_router

all_routes = Blueprint("all_routes", __name__)

all_routes.register_blueprint(auth_router)
all_routes.register_blueprint(profile_router)
all_routes.register_blueprint(resume_router)
all_routes.register_blueprint(favorite_router)
all_routes.register_blueprint(filter_router)
all_routes.register_blueprint(job_router)
all_routes.register_blueprint(employer_jobs_router)
all_routes.register_blueprint(finder_jobs_router)