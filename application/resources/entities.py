from flask_restful import Resource, reqparse, abort

from application.db.entities import create_new_entity, delete_entity_by_id, get_entity_by_prop, update_entity
from application.resources import to_json, replace_id
from application.token_validation import requires_auth, get_saved_token

new_entity_parser = reqparse.RequestParser()
new_entity_parser.add_argument('modelId', required=True, trim=True, help='Model ID must contain a value.')
new_entity_parser.add_argument('name', required=True, trim=True, help='Entity name must contain a value.')
new_entity_parser.add_argument('description', nullable=True, trim=True)
new_entity_parser.add_argument('isActive', nullable=False, type=bool)

update_entity_parser = reqparse.RequestParser()
update_entity_parser.add_argument('modelId', required=True, trim=True, help='Model ID must contain a value.')
update_entity_parser.add_argument('entityId', required=True, trim=True, help='Entity ID must contain a value.')
update_entity_parser.add_argument('name', required=True, trim=True, help='Entity name must contain a value.')
update_entity_parser.add_argument('description', nullable=True, trim=True)
update_entity_parser.add_argument('isActive', nullable=False, type=bool)


class EntityWithId(Resource):
    @requires_auth
    def get(self, entity_id):
        entity_result = [entity for entity in get_entity_by_prop('id', entity_id)]
        if not entity_result or not len(entity_result):
            return abort(404, message='Could not find entity with ID in database.')

        entity = entity_result[0]

        return to_json(replace_id(entity)), 200

    @requires_auth
    def delete(self, entity_id):
        res = delete_entity_by_id(entity_id)
        if not res.get('updatedExisting'):
            return abort(500, message='Failed to delete entity.')

        return '', 204


class Entities(Resource):
    @requires_auth
    def post(self):
        args = new_entity_parser.parse_args()
        user_token = get_saved_token()
        user_email = user_token.get('emails')[0]

        entity_name = args.get('name')
        entity_result = [entity for entity in get_entity_by_prop('name', entity_name, args.get('modelId'))]
        if entity_result:
            return abort(400, message=f'Entity with name "{entity_name}" already exists.')

        res = create_new_entity(
            args.get('modelId'),
            args.get('name'),
            args.get('description'),
            args.get('isActive'),
            user_email)

        if not res.get('updatedExisting'):
            return abort(500, message='Failed to update entity.')

        return res['id'], 201

    @requires_auth
    def put(self):
        args = update_entity_parser.parse_args()
        user_token = get_saved_token()
        user_email = user_token.get('emails')[0]
        entity_id = args.get('entityId')
        entity_name = args.get('name')
        entity_result = [entity for entity in get_entity_by_prop('name', entity_name)]
        if not entity_result or not len(entity_result):
            return abort(404, message='Could not find entity with ID in database.')

        entity = entity_result[0]['entities'][0]
        if entity and entity['id'] != entity_id:
            return abort(400, message=f'Entity with name "{entity_name}" already exists.')

        res = update_entity(entity_id, args.get('name'), args.get('description'), args.get('isActive'), user_email)
        if not res.modified_count == 1:
            return abort(500, message='Failed to update entity.')

        return '', 204
