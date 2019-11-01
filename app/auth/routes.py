from flask import Flask, request, jsonify, Blueprint
from auth.auth import create_app, authorize
from werkzeug.exceptions import BadRequest, Unauthorized, BadRequestKeyError


auth_app = Blueprint('auth_app', __name__)


@auth_app.route('/auth/registerapp', methods=['POST'])
def register_app():
    username = request.headers.get('username')
    password = request.headers.get('password')
    app_name = (request.form or {}).get('app_name')

    if not username:
        raise BadRequestKeyError("username should be provided in the header")

    if not password:
        raise BadRequestKeyError("password should be provided in the header")

    if not app_name:
        raise BadRequest("app_name must me provided in request body")

    result = create_app(username, password, app_name)

    if result == 0:
        raise Unauthorized("username/password did not match.")

    return jsonify({'app_id': result.app_id,
                    'app_name': result.app_name,
                    'app_key': result.app_key})
