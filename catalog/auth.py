from flask import Blueprint, request, current_app
from farmer.rest import handle, make_token
from farmer.errors import AuthException

auth = Blueprint("auth", __name__, url_prefix="/auth")

@auth.route('/', methods=["POST"])
@handle(code=201)
def authenticate():
    cred = request.json
    user = current_app.config['DEFAULT_USER'] == cred.get('user', '')
    passwd = current_app.config['DEFAULT_PASS'] == cred.get('pass', '')
    if user and passwd:
        token = make_token({'user': cred.get('user')}).decode()
        return token

    raise AuthException('invalid credentials provided')
