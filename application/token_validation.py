# Format error response and append status code
import json
from functools import wraps
from urllib.request import urlopen
from jose import jwt
from flask import request, current_app, g

ALGORITHMS = ["RS256"]


def get_token_auth_header():
    auth = request.headers.get("Authorization", None)
    if not auth:
        raise AuthError({"code": "authorization_header_missing",
                        "description":
                            "Authorization header is expected"}, 401)

    parts = auth.split()

    if parts[0].lower() != "bearer":
        raise AuthError({"code": "invalid_header",
                        "description":
                            "Authorization header must start with"
                            " Bearer"}, 401)
    elif len(parts) == 1:
        raise AuthError({"code": "invalid_header",
                        "description": "Token not found"}, 401)
    elif len(parts) > 2:
        raise AuthError({"code": "invalid_header",
                        "description":
                            "Authorization header must be"
                            " Bearer token"}, 401)

    token = parts[1]
    return token


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_auth_header()
        jsonurl = urlopen(current_app.config['MSAL_DISCOVERY'])
        jwks = json.loads(jsonurl.read())
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
        if rsa_key:
            try:
                res = jwt.decode(
                    token,
                    rsa_key,
                    options={'verify_nbf': False},
                    algorithms=ALGORITHMS,
                    audience=current_app.config['MSAL_AUDIENCE'],
                    issuer="https://mihste.b2clogin.com/ff0c17b4-8ed8-4679-80e0-a0997658611e/v2.0/"
                )

                if not res['emails']:
                    raise AuthError({"code": "invalid_data",
                                     "description": "Bearer token is missing email address value."}, 400)

                if res['scp'] != 'ReadWrite':
                    raise AuthError({
                        "code": "missing_scope",
                        "description": "You don't have access to this resource"
                    }, 403)

                g.token = res
            except jwt.ExpiredSignatureError:
                raise AuthError({"code": "token_expired",
                                "description": "token is expired"}, 401)
            except jwt.JWTClaimsError:
                raise AuthError({"code": "invalid_claims",
                                "description":
                                    "incorrect claims,"
                                    "please check the audience and issuer"}, 401)
            except Exception:
                raise AuthError({"code": "invalid_header",
                                "description":
                                    "Unable to parse authentication"
                                    " token."}, 401)

            return f(*args, **kwargs)
        raise AuthError({"code": "invalid_header",
                        "description": "Unable to find appropriate key"}, 401)
    return decorated


def get_saved_token():
    token = g.token
    if not token:
        return AuthError({"code": "missing_token", "description": "Bearer token missing"}, 401)

    email = token.get('emails')
    if not email:
        return AuthError({"code": "missing_email", "description": "Bearer token missing"}, 400)

    return token


def requires_scope(required_scope):
    def wrapper(f):
        @wraps(f)
        def wrapped_f(*args, **kwargs):
            token = get_token_auth_header()
            unverified_claims = jwt.get_unverified_claims(token)
            if unverified_claims.get("scp"):
                token_scopes = unverified_claims["scp"].split()
                for token_scope in token_scopes:
                    if token_scope == required_scope:
                        return f(args, kwargs)

        return wrapped_f
    return wrapper


class AuthError(Exception):
    def __init__(self, json_obj, code):
        self.json_obj = json_obj
        self.code = code
