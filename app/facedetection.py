from flask import Flask, request, jsonify, Blueprint
import utils as df
from auth.auth import authorize
from db.database import connect_db
from auth.routes import auth_app
from errors import errors
from worker import make_celery


app = Flask(__name__)

app.config['CELERY_BROKER_URL'] = 'pyamqp://localhost:5672/'
app.config['CELERY_RESULT_BACKEND'] = 'db+postgresql+psycopg2://postgres:@localhost/postgres'
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
    user = request.json
    id = user.get('id')
    image = user.get('image')

    msg = df.save_image_in_db(id, image)

    if isinstance(msg, int):
        out = {'status': 'success', 'message': 'image saved in db for user {}'.format(id)}

    return jsonify(out)


@app.route('/compareimage', methods=['POST'])
@authorize(request=request)
def compare_image():
    image = request.json.get('image')

    result = df.compare_image_in_db(image)
    out = {'status': 'success', 'message': result}

    return jsonify(out)


@app.route('/validateimage', methods=['POST'])
@authorize(request=request)
def validate_image():
    image = request.json.get('image')
    result = df.get_facial_landmarks(image)
    out = {'status': 'success', 'message': 'image identified'}

    return jsonify(out)


@app.route('/asynccompareimage', methods=['POST'])
@authorize(request=request)
def async_compare_image():
    image = request.json.get('image')
    result = async_compare.delay(image)
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
def async_compare(img_data):
    result = df.compare_image_in_db(img_data)
    return result


if __name__ == "__main__":
    app.register_blueprint(auth_app)
    app.register_blueprint(errors)
    app.run(debug=True)
