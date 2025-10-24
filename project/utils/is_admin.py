from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from project.domain.admin.admin_dal import AdminDal


def admin_required():
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorator(*args, **kwargs):
            user_id = get_jwt_identity()
            data_state = AdminDal.is_admin(user_id)
            if not data_state:
                return data_state.to_response()
            if not data_state.data:
                return jsonify({"error": "Admin access required"}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper
