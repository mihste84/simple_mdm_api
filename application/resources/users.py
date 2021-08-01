import json
from bson import json_util, ObjectId
from email_validator import validate_email
from flask_restful import Resource, reqparse, abort

from application.token_validation import requires_auth
from application.db import mongo

users_parser = reqparse.RequestParser()
users_parser.add_argument('search_term', nullable=True)
users_parser.add_argument('sort_column', nullable=True)
users_parser.add_argument('sort_order', nullable=True)
users_parser.add_argument('page', nullable=True)
users_parser.add_argument('page_size', nullable=True)


def email(email_str):
    if validate_email(email_str, check_deliverability=False):
        return email_str
    else:
        raise ValueError('{} is not a valid email'.format(email_str))


def to_json(data):
    return json.loads(json_util.dumps(data))


user_parser = reqparse.RequestParser()
user_parser.add_argument('first_name', required=True)
user_parser.add_argument('last_name', required=True)
user_parser.add_argument('e_mail', type=email, required=True)
user_parser.add_argument('country', required=True)
user_parser.add_argument('ssn', type=int, required=True)
user_parser.add_argument('description')
user_parser.add_argument('start_date', required=True)
user_parser.add_argument('id')


class Users(Resource):
    @requires_auth
    def get(self):
        args = users_parser.parse_args()
        regex = {'$regex': f'^{args["search_term"]}.*', '$options': 'i'}
        query = {'$or': [
            {'first_name': regex},
            {'last_name': regex}
        ]}

        page = int(args['page']) if args['page'] else 1
        page_size = int(args['page_size']) if args['page_size'] else 20
        skips = page_size * (page - 1)

        data = (
            [user for user in mongo.db.users.find(query).sort(args['sort_column'], int(args['sort_order'])).skip(skips).limit(page_size)],
            mongo.db.users.find(query).count()
        )
        return to_json(data), 200


class UserCreate(Resource):
    @requires_auth
    def put(self):
        args = user_parser.parse_args()
        object_id = ObjectId(args['id']) if args['id'] else ''
        res = mongo.db.users.replace_one({"_id": object_id}, args, upsert=True)
        if not res.acknowledged:
            return abort(404, message="User doesn't exist in database.")

        return res.upserted_id, 201 if res.upserted_id else 204


class User(Resource):
    @requires_auth
    def get(self, user_id):
        user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            return abort(404, message="User doesn't exist in database.")

        return to_json(user)

    @requires_auth
    def delete(self, user_id):
        deleted = mongo.db.users.delete_one({"_id": ObjectId(user_id)})
        if not deleted.acknowledged:
            return abort(404, message="User doesn't exist in database.")

        return '', 204
