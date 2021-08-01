from flask_restful import Resource, reqparse

from application.token_validation import requires_auth

new_attribute_parser = reqparse.RequestParser()


class Attributes(Resource):
    @requires_auth
    def post(self, entity_id):
        return '', 201
