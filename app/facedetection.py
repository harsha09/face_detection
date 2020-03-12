from flask import Flask, request, jsonify
import utils as df
from auth.auth import authorize
from auth.routes import auth_app
from errors import errors
from worker import make_celery
from werkzeug.exceptions import BadRequest
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
    user = df.get_request_data(request)
    id = user.get('id')
    image = user.get('image')

    if (not id) or (not image):
        raise BadRequest(
            'Invalid request body, id and image should be specified.')

    msg = df.save_image_in_db(id, image, request.headers.get('app_id'))

    if isinstance(msg, int):
        out = {'status': 'success',
               'message': 'image saved in db for user {}'.format(id)}

    return jsonify(out)


@app.route('/deleteimage/<string:image_id>', methods=['DELETE'])
@authorize(request=request)
def delete_image(image_id):
    appid = request.headers.get('app_id')
    cnt = df.delete_images(image_id, appid)
    out = {'status': 'success',
    'message': 'image {} has been deleted.'.format(image_id)}
    return jsonify(out)


@app.route('/deleteimages', methods=['DELETE'])
@authorize(request=request)
def delete_images():
    appid = request.headers.get('app_id')
    image_ids = []
    try:
        image_ids = df.get_request_data(request).get('images', '').split(',')
    except AttributeError as ae:
        image_ids = []

    cnt = df.delete_images(image_ids, appid)
    out = {'status': 'success',
    'message': 'images are deleted.'}
    return jsonify(out)


@app.route('/compareimage', methods=['POST'])
@authorize(request=request)
def compare_image():
    image = df.get_request_data(request).get('image')

    if (not image):
        raise BadRequest('Invalid request body. image shoud be specified.')

    result = df.compare_image_in_db(image, request.headers.get('app_id'))
    out = {'status': 'success', 'message': result}

    return jsonify(out)


@app.route('/comparelive', methods=['POST'])
@authorize(request=request)
def compare_live():
    request_data = df.get_request_data(request)
    images = request_data.get('images')
    pattern = request_data.get('pattern', 'open-close-open')

    if (not images) or (not isinstance(images, list)):
        raise BadRequest('Invalid request body. List of images shoud be specified.')

    result, pattern = df.compare_live_image(images, request.headers.get('app_id'))
    out = {'status': 'success', 'message': result, 'pattern': pattern}

    return jsonify(out)


@app.route('/comparedpcamimages', methods=['POST'])
@authorize(request=request)
def compare_dp_cam_images():
    request_data = df.get_request_data(request)
    dp = request_data.get('display_picture')
    cam_pic = request_data.get('cam_picture')

    if (not dp) or (not cam_pic):
        raise BadRequest('Invalid request body. display_picture and cam_picture should be sent.')

    result = df.compare_dp_cam_images(dp, cam_pic)
    out = {'status': 'success', 'message': result}

    return jsonify(out)


@app.route('/validateimage', methods=['POST'])
@authorize(request=request)
def validate_image():
    image = df.get_request_data(request).get('image')

    if not image:
        raise BadRequest('Invalid request body. image shoud be specified.')

    result = df.get_facial_landmarks(image)

    out = {'status': 'success', 'message': 'image identified'}

    return jsonify(out)


@app.route('/asynccompareimage', methods=['POST'])
@authorize(request=request)
def async_compare_image():
    image = df.get_request_data(request).get('image')

    if not image:
        raise BadRequest('Invalid request body. image shoud be specified.')

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
