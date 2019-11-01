from flask import Flask, request, jsonify
import utils as df
from auth.auth import authorize
from auth.routes import auth_app
from errors import errors
from worker import make_celery
import os


app = Flask(__name__)

rabbitmq_port = os.getenv('RABBITMQ_PORT')
debug = os.getenv('DEBUG')

app.config['CELERY_BROKER_URL'] = f'pyamqp://rabbitmq:{rabbitmq_port}/'
app.config['CELERY_RESULT_BACKEND'] = 'db+postgresql+psycopg2://postgres:@db/postgres'
celery = make_celery(app)

app.register_blueprint(auth_app)
app.register_blueprint(errors)


@app.route("/")
@authorize(request=request)
def test():
    return "Running"


@app.route('/storeimage', methods=['POST'])
@authorize(request=request)
def store_image():
    user = (request.form or {})
    id = user.get('id')
    image = user.get('image')

    msg = df.save_image_in_db(id, image)

    if isinstance(msg, int):
        out = {'status': 'success',
               'message': 'image saved in db for user {}'.format(id)}

    return jsonify(out)


@app.route('/compareimage', methods=['POST'])
@authorize(request=request)
def compare_image():
    image = (request.form or {}).get('image')
    appid = request.headers.get('app_id')
    result = df.compare_image_in_db(image, appid)
    out = {'status': 'success', 'message': result}

    return jsonify(out)


@app.route('/validateimage', methods=['POST'])
@authorize(request=request)
def validate_image():
    image = (request.form or {}).get('image')
    result = df.get_facial_landmarks(image)
    out = {'status': 'success', 'message': 'image identified'}

    return jsonify(out)


@app.route('/asynccompareimage', methods=['POST'])
@authorize(request=request)
def async_compare_image():
    image = (request.form or {}).get('image')
    appid = request.headers.get('app_id')
    result = async_compare.delay(image, appid)
    out = {'status': 'success', 'request_id': result.id}

    return jsonify(out)


@app.route('/status/<request_id>', methods=['GET'])
@authorize(request=request)
def compare_image_status(request_id):
    task = async_compare.AsyncResult(request_id)
    out = {'status': task.state}

    if task.state == 'FAILURE':
        out['message'] = str(task.info)

    if task.state == 'SUCCESS':
        out['message'] = task.result

    return jsonify(out)


@celery.task()
def async_compare(img_data, appid):
    result = df.compare_image_in_db(img_data, appid)
    return result


if __name__ == "__main__":
    app.register_blueprint(auth_app)
    app.register_blueprint(errors)
    app.run(debug=debug)
