from flask_httpauth import HTTPBasicAuth, HTTPDigestAuth, HTTPTokenAuth
from werkzeug.exceptions import BadRequest
from flask import request, jsonify, make_response
from utils import get_user, make_error
import functools
import secrets

#auth = HTTPDigestAuth()
#auth = HTTPBasicAuth()
#auth = HTTPTokenAuth(scheme='Bearer')


#@auth.verify_token
#def verify_tokens(token):
#    user = get_user(token=token)
#    if not(user is None):
#        return user


def create_token(length=64):
    return secrets.token_hex(length)


# decorator to parse json requests and handle errors
def verify_token(f=None, decrypt=True, encrypt=True, role=None):
    assert callable(f) or f is None
    def _decorator(func):
        @functools.wraps(func)
        def wrapper(*args):
            try:
                data = request.get_json()
            except Exception as e:
                return make_error(500)
            if ('token' in data):
                user = get_user(token=data['token'])
                if user:
                    if not(role is None):
                        if user.role < role:
                            return make_error(403)
                    return func(*args, user, data)
                else:
                    return make_error(401)
            else:
                return make_error(400)
        return wrapper
    return _decorator(f) if callable(f) else _decorator
