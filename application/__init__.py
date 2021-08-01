from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_restful import Api

from application.db import mongo
from application.errors import NotFoundError
from application.resources.attributes import Attributes
from application.resources.entities import Entities, EntityWithId
from application.resources.master_data import UserMasterData, UserMasterDataWithId
from application.resources.model_admin import ModelAdmin
from application.resources.users import Users, User, UserCreate
from application.token_validation import AuthError
from flask_cors import CORS

api = Api(prefix='/api')
jwt = JWTManager()


def init_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    with app.app_context():
        # api.add_resource(Users, '/users')
        # api.add_resource(User, '/user/<string:user_id>')
        api.add_resource(UserMasterDataWithId, '/userMasterData/<model_id>')
        api.add_resource(UserMasterData, '/userMasterData')
        api.add_resource(EntityWithId, '/entities/<entity_id>')
        api.add_resource(Entities, '/entities')
        api.add_resource(ModelAdmin, '/modelAdmin')
        api.add_resource(Attributes, '/attributes/<entity_id>')

        api.init_app(app)
        jwt.init_app(app)
        mongo.init_app(app)
        CORS(app)

        @app.errorhandler(Exception)
        def handle_exception(e):
            vars(e)
            return jsonify(error=str(e)), 500

        @app.errorhandler(AuthError)
        def handle_exception(e):
            vars(e)
            return jsonify(error=e.json_obj), e.code

        @app.errorhandler(NotFoundError)
        def handle_exception(e):
            vars(e)
            return jsonify(error=str(e)), 404

        return app
