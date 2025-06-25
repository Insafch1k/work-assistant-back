from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
#from project.models.profile import ProfileInitRequest, ProfileInitResponse
from project.DAL.auth_dal import AuthDAL
from project.BL.auth_bl import validate_register, get_user_data

auth_router = Blueprint("auth_router", __name__)


@auth_router.route("/profile/init", methods=["POST"])
def register():
    #data = ProfileInitRequest.model_validate(request.json)
    data = request.get_json()
    result = validate_register(data)

    if result["status"] == "error":
        return jsonify(result), 400

    temp_data = AuthDAL.add_user(data["tg"], data["user_role"], data["user_name"])
    print(temp_data)
    user = get_user_data(temp_data)
    if data["user_role"] == "finder":
        AuthDAL.add_finder(list(user.values())[0])
    if data["user_role"] == "employer":
        AuthDAL.add_employer(list(user.values())[0])

    #response = ProfileInitResponse(**user)
    #return jsonify(response.model_dump()), 201

    access_token = create_access_token(identity=str(data["tg"]))
    return jsonify({"message": "Вы успешно зарегистрированы"}), 200

@auth_router.route("/profile/login", methods=["POST"])
def login():
    data = request.get_json()

    access_token = create_access_token(identity=str(data["tg"]))
    return jsonify(access_token=access_token), 200