from flask import Blueprint, Response
from werkzeug.exceptions import HTTPException
import json


errors = Blueprint('errors', __name__)


@errors.app_errorhandler(HTTPException)
def catch_http_exception(e):
    response = Response()
    response.data = json.dumps({
        'status': 'failure',
        'message': e.description,
        'code': e.code
    })
    response.content_type = 'application/json'

    return response, e.code


@errors.app_errorhandler(Exception)
def catch_exception(e):
    response = Response()
    response.data = json.dumps({
        'status': 'failure',
        'message': str(e),
        'code': 500
    })
    response.content_type = 'application/json'

    return response, 500
