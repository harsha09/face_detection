import face_recognition as fd
from PIL import Image
import numpy as np
import dlib
import face_recognition_models
import math
from base64 import urlsafe_b64decode
from io import BytesIO
from db.database import connect_db
from werkzeug.exceptions import NotFound, BadRequest
import json


face_recognition_model = face_recognition_models.face_recognition_model_location()
face_encoder = dlib.face_recognition_model_v1(face_recognition_model)
face_detector = dlib.get_frontal_face_detector()

predictor_68_point_model = face_recognition_models.pose_predictor_model_location()
pose_predictor_68_point = dlib.shape_predictor(predictor_68_point_model)

predictor_5_point_model = face_recognition_models.pose_predictor_five_point_model_location()
pose_predictor_5_point = dlib.shape_predictor(predictor_5_point_model)


def get_request_data(request):
    data = request.json or request.form
    if not data:
        try:
            data = json.loads(data.get_data() or '{}')
        except json.JSONDecodeError as ex:
            raise BadRequest('Not a proper json {}'.format(str(ex)))

    return data or {}


def _rect_to_css(rect):
    """
    Convert a dlib 'rect' object to a plain tuple in (top, right, bottom, left) order
    :param rect: a dlib 'rect' object
    :return: a plain tuple representation of the rect in (top, right, bottom, left) order
    """
    return rect.top(), rect.right(), rect.bottom(), rect.left()


def _css_to_rect(css):
    """
    Convert a tuple in (top, right, bottom, left) order to a dlib `rect` object
    :param css:  plain tuple representation of the rect in (top, right, bottom, left) order
    :return: a dlib `rect` object
    """
    return dlib.rectangle(css[3], css[0], css[1], css[2])


def _trim_css_to_bounds(css, image_shape):
    """
    Make sure a tuple in (top, right, bottom, left) order is within the bounds of the image.
    :param css:  plain tuple representation of the rect in (top, right, bottom, left) order
    :param image_shape: numpy shape of the image array
    :return: a trimmed plain tuple representation of the rect in (top, right, bottom, left) order
    """
    return max(css[0], 0), min(css[1], image_shape[1]), min(css[2], image_shape[0]), max(css[3], 0)


def raw_face_landmarks(face_image, model="large"):
    face_locations = face_detector(face_image, 0.8)
    pose_predictor = pose_predictor_68_point

    if model == "small":
        pose_predictor = pose_predictor_5_point

    return [pose_predictor(face_image, face_location) for face_location in face_locations]


def compress_base64image(image_data):
    """Decodes and compress the base64 encoded image.

    Parameters:
    image_data (string): base64 encoded image string

    Returns:
    np.array: image data
    """

    img = Image.open(BytesIO(urlsafe_b64decode(image_data)))
    size = 240
    w, h = size, math.ceil(size * img.height/img.width)
    img = img.resize((w, h), Image.ANTIALIAS)

    return np.array(img)


def get_facial_landmarks(image_data):
    """Locates the facial landmarks in image, like eyes, nose, mouth etc.

    Parameters:
    image_data (string): base64 encoded image string

    Returns:

    """
    compressed_image = compress_base64image(image_data)
    landmarks = fd.face_landmarks(compressed_image)

    if not landmarks:
        raise BadRequest("No Face found")

    if len(landmarks) > 1:
        raise BadRequest("{} Faces found".format(len(landmarks)))

    return landmarks


def get_face_encoding(image_data):
    """ """

    image_compressed = compress_base64image(image_data)
    landmarks = raw_face_landmarks(image_compressed)

    if not landmarks:
        raise BadRequest("No Face found")

    if len(landmarks) > 1:
        raise BadRequest("{} Faces found".format(len(landmarks)))

    face_encoding = [np.array(face_encoder.compute_face_descriptor(
        image_compressed, l, 1)) for l in landmarks][0]

    return '({})'.format(', '.join([str(i) for i in face_encoding]))


def determine_eye_blink(facial_landmark):
    ear_func = lambda eye: (abs(eye[1] - eye[5]) + abs(eye[2] - eye[4])) / 2 * abs(eye[0] - eye[3])
    left_ear = ear_func(facial_landmark.get('left_eye'))
    right_ear = ear_func(facial_landmark.get('right_ear'))

    if (left_ear + right_ear) / 2.0 < 0.28:
        return 'close'

    return 'open'


@connect_db
def compare_live_image(images, appid):
    facial_landmarks = [get_facial_landmarks(i) for i in images]
    found_pattern = '-'.join([determine_eye_blink(i) for i in facial_landmarks])

    opened_eye_index = 0

    try:
        opened_eye_index = found_pattern.index('open')
    except ValueError as ve:
        raise NotFound("No image with open eye found")

    face_encoding = get_face_encoding(images[opened_eye_index])
    query = "select id from im_data where (data <-> '%s'::cube) < 0.5 and appid = '%s'" % (
        face_encoding, appid)

    cursor.execute(query)
    record = cursor.fetchone()

    if not record:
        raise NotFound("No image Found in database")

    return record[0], found_pattern


@connect_db
def save_image_in_db(id, image_data, appid, cursor=None, con=None):
    face_encoding = get_face_encoding(image_data)
    query = 'insert into im_data(id, data, appid) values (%s, %s, %s)'
    cursor.execute(query, (id, face_encoding, appid))
    con.commit()
    return cursor.rowcount


@connect_db
def compare_image_in_db(image_data, appid, con=None, cursor=None):
    face_encoding = get_face_encoding(image_data)
    query = "select id from im_data where (data <-> '%s'::cube) < 0.5 and appid = '%s'" % (
        face_encoding, appid)

    cursor.execute(query)
    record = cursor.fetchone()

    if not record:
        raise NotFound("No image Found in database")

    return record[0]

