import psycopg2
from psycopg2 import pool
from functools import wraps
import os

postgres_port = os.getenv('POSTGRES_PORT')
facerecog_db = os.getenv('POSTGRES_DB')
db_host = os.getenv('DB_HOST')

db_pool = psycopg2.pool.ThreadedConnectionPool(1, 10, user="facerecog",
                                               password="ideeo@519",
                                               host=db_host,
                                               port=postgres_port,
                                               database=facerecog_db)


def connect_db(func):
    con = db_pool.getconn()
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = None
        with con.cursor() as cursor:
            result = func(cursor=cursor, con=con, *args, **kwargs)
        # finally:
        #     db_pool.putconn(con)
        return result
    return wrapper


def get_db_con():
    db_con = db_pool.getconn()
    return db_con


def put_con(con, *args, **kwargs):
    db_pool.putconn(con, *args, **kwargs)
