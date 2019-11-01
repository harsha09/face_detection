from flask import Flask, request, jsonify, Blueprint
from auth.auth import create_app, authorize
from werkzeug.exceptions import BadRequest, Unauthorized


auth_app = Blueprint('auth_app', __name__)


@auth_app.route('/auth/registerapp', methods=['PUT'])
def register_app():
    username = request.headers.get('username')
    password = request.headers.get('password')
    app_name = request.json.get('app_name')

    if (not username) or (not password) or (not app_name):
        raise BadRequest(
            "One or many params(username, password, app_name) are not set.")

    result = create_app(username, password, app_name)

    if result == 0:
        raise Unauthorized("username/password did not match.")

    return jsonify({'app_id': result.app_id,
                    'app_name': result.app_name,
                    'app_key': result.app_key})
