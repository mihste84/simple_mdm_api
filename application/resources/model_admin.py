from flask_restful import Resource, abort, reqparse

from application.db.master_data import delete_admin, add_new_admin, get_model_admins_by_id
from application.db.users import get_user_by_email
from application.resources import is_user_model_admin
from application.token_validation import requires_auth

admin_parser = reqparse.RequestParser()
admin_parser.add_argument('modelId', required=True, trim=True, help='Model ID must contain a value.')
admin_parser.add_argument('adminEmail', required=True, trim=True, help='Admin email must contain a value.')


class ModelAdmin(Resource):
    @requires_auth
    def delete(self):
        args = admin_parser.parse_args()
        model_id = args.get('modelId')
        if not is_user_model_admin(model_id):
            return abort(403, message='User is not authorized to perform action on this model.')

        res = delete_admin(model_id, args.get('adminEmail'))
        if not res.get('updatedExisting'):
            return abort(500, message='Failed to remove admin from model.')
        return '', 204

    @requires_auth
    def post(self):
        args = admin_parser.parse_args()
        model_id = args.get('modelId')

        if not is_user_model_admin(model_id):
            return abort(403, message='User is not authorized to perform action on this model.')

        admin_email = args.get('adminEmail')

        model_admin = get_model_admins_by_id(model_id)
        if admin_email in model_admin.get('admins'):
            return abort(400, message='User is already admin for this model.')

        user = get_user_by_email(admin_email)
        if not user:
            send_email(admin_email)

        res = add_new_admin(model_id, admin_email)
        if not res.get('updatedExisting'):
            return abort(500, message='Failed to add admin to model.')

        return '', 201


def send_email(admin_email):
    return True
