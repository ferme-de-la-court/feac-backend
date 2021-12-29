from functools import wraps
from authlib.jose import jwt
from flask import request, jsonify, current_app, request, g
from farmer.errors import RestException

_bearer = 'Bearer '

def handle(code=200):
    name = ''
    def decorate(func):
        nonlocal name
        name = func.__name__
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                data = func(*args, **kwargs)
            except RestException as e:
                msg = {
                    "error": str(e),
                    "code": e.code,
                }
                return jsonify(msg), e.code
            except Exception as e:
                msg = {
                    "error": str(e),
                    "code":  400,
                }
                return jsonify(msg), 400
            else:
                if not data:
                    return '', 204
                return jsonify(data), 201

        return wrapper

    decorate.__name__ = f'decorate_{name}'
    return decorate


def make_token(payload):
    """create a JWT token"""
    header = {'alg': 'HS256'}
    body = {'iss': current_app.config["JWT_ISSUER"]}
    body = body.update(payload)
    return jwt.encode(header, payload, current_app.config["SECRET_KEY"])


def cors(resp):
    """set CORS headers"""
    resp.access_control_allow_origin = "*"
    resp.access_control_allow_methods = "GET", "OPTIONS", "PUT", "POST", "DELETE"
    resp.access_control_allow_headers = "Accept", "Accept-Language", "Content-Language", "Origin", "Content-Type"
    return resp


def check_token():
    """check that Authorization header as a valid JWT token"""
    if cred := request.authorization:
        if cred.username == current_app.config['DEFAULT_USER'] and cred.password == current_app.config['DEFAULT_PASS']:
            g.user = cred.username
            return None
        return "", 401

    token = request.headers.get('Authorization', '')
    if not token:
        return "", 403

    try:
        x = token.index(_bearer)
        if x < 0:
            raise ValueError('missing Bearer')
        token = token[len(_bearer):]
    except ValueError:
        return "", 403

    try:
        claims = jwt.decode(token, current_app.config['SECRET_KEY'])
    except Exception:
        return "", 401
    else:
        g.user = claims.get('user', '')


def generate_token(resp):
    """set the Authorization header with a valid JWT token for next request(s)"""
    if resp.status_code >= 400:
        return resp


    if not g.user:
        resp.status_code = 403
        return resp

    token = make_token({'user': g.user})
    resp.headers['Authorization'] = f'{_bearer}{token}'
    return resp
