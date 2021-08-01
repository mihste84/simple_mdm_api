import json
from bson import json_util

from application.db.master_data import get_model_admins_by_id
from application.token_validation import get_saved_token


def to_json(data):
    dumps = json_util.dumps(data)
    json_obj = json.loads(dumps)

    return json_obj


def replace_id(obj):
    obj['id'] = str(obj.get('_id'))
    del obj['_id']
    return obj


def is_user_model_admin(model_id):
    user_token = get_saved_token()
    user_email = user_token.get('emails')[0]
    model_admin = get_model_admins_by_id(model_id)
    if user_email not in model_admin.get('admins'):
        return None

    return user_email
