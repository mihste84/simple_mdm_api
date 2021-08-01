from flask_restful import Resource, abort, reqparse
from application.db.master_data import get_models_by_user_email, create_new_model, delete_model_by_id, update_model, \
    get_model_by_id
from application.db.users import get_user_by_email, create_new_user
from application.resources import to_json, replace_id, is_user_model_admin
from application.token_validation import requires_auth, get_saved_token

new_model_parser = reqparse.RequestParser()
new_model_parser.add_argument('name', required=True, trim=True, help='Model name must contain a value.')
new_model_parser.add_argument('description', nullable=True, trim=True)
new_model_parser.add_argument('isActive', nullable=False, type=bool)

edit_model_parser = reqparse.RequestParser()
edit_model_parser.add_argument('name', required=True, trim=True, help='Model name must contain a value.')
edit_model_parser.add_argument('description', nullable=True, trim=True)
edit_model_parser.add_argument('isActive', nullable=False, type=bool)
edit_model_parser.add_argument('id', required=True)


class UserMasterDataWithId(Resource):
    @requires_auth
    def delete(self, model_id):
        if not is_user_model_admin(model_id):
            return abort(403, message='User is not authorized to perform action on this model.')

        res = delete_model_by_id(model_id)
        if not res.acknowledged:
            raise abort(500, message='Failed to delete  model.')

        return '', 204

    @requires_auth
    def get(self, model_id):
        if not is_user_model_admin(model_id):
            return abort(403, message='User is not authorized to perform action on this model.')

        model = [replace_id(model) for model in get_model_by_id(model_id)]
        if not model:
            return abort(404, message='Could not find any models with ID.')

        return to_json(model[0]), 200


class UserMasterData(Resource):
    @requires_auth
    def get(self):
        user_token = get_saved_token()
        user_email = user_token.get('emails')[0]
        user = get_user_by_email(user_email)
        if not user:
            username = user_token.get('name')
            res = create_new_user(username, user_email)
            if res.acknowledged:
                user = {'email': user_email, 'username': username, '_id': res.inserted_id}
            else:
                return abort(500, message="Failed to create new user in database.")

        models = [replace_id(model) for model in get_models_by_user_email(user_email)]

        user['models'] = models

        return to_json(replace_id(user)), 200

    @requires_auth
    def post(self):
        args = new_model_parser.parse_args()
        user_token = get_saved_token()
        user_email = user_token.get('emails')[0]

        res = create_new_model(args.get('name'), args.get('description'), args.get('isActive'), user_email)
        if not res.acknowledged:
            raise abort(500, message='Failed to insert new model.')

        return str(res.inserted_id), 201

    @requires_auth
    def put(self):
        args = edit_model_parser.parse_args()

        user_email = is_user_model_admin(args.get('id'))
        if not user_email:
            return abort(403, message='User is not authorized to perform action on this model.')

        res = update_model(args.get('id'), args.get('name'), args.get('description'), args.get('isActive'), user_email)
        if not res.acknowledged:
            raise abort(500, message='Failed to update model.')

        return '', 204
