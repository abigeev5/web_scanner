from flask import jsonify, make_response
from models import User
import db_session


error_codes = {
    400: 'Bad request',
    401: 'Unauthorized',
    403: 'No permission',
    404: 'User not found',
    409: 'User already exist',
    500: 'Unknown error'
}


def get_user(id=None, username=None, token=None):
    session = db_session.create_session()
    response = None
    if not(id is None):
        response = session.query(User).filter(User.id == id).first()
    elif not(token is None):
        response = session.query(User).filter(User.token == token).first()
    else:
        response = session.query(User).filter(User.username == username).first()
    session.close()
    return response


def make_error(code):
    return make_response(jsonify({'Error': error_codes[code]}), code)

def make_success(code):
    return make_response(jsonify({'Result': 'Ok'}), code)

def get_error_json(code):
    return ({'Error': error_codes[code]}, code)
