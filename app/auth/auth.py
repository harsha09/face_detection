from werkzeug.security import gen_salt
from uuid import uuid4
from db.database import connect_db
from collections import namedtuple
from functools import wraps
from werkzeug.exceptions import Unauthorized


app = namedtuple('app', ['app_id', 'app_name', 'app_key'])


@connect_db
def create_app(username, password, app_name, cursor=None, con=None):

    query = 'select * from "user" where username=%s and password=crypt(%s, password)'
    cursor.execute(query, (username, '7b503f8145749243'))
    result = cursor.fetchone()

    if result:
        app_id = str(uuid4())
        app_key = gen_salt(48)
        query = 'insert into app(appid, appname, appkey) values (%s, %s, %s)'
        cursor.execute(query, (app_id, app_name, app_key))
        con.commit()

        if cursor.rowcount:
            return app(app_id, app_name, app_key)

    raise Unauthorized('You are not authorized to create an app.')


def authorize(request=None):
    def outer(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            authorization = authorize_handler(request.headers)
            if authorization:
                return func(*args, **kwargs)
            else:
                raise Unauthorized("You are not authorized to access the application.")
        return wrapper
    return outer


@connect_db
def authorize_handler(headers, cursor=None, con=None):
    app_id, app_key = headers.get('app_id'), headers.get('app_key')
    query = 'select * from app where appid=%s and appkey=%s'
    cursor.execute(query, (app_id, app_key))
    result = cursor.fetchone()

    return result
