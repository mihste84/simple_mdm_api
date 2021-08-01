from flask import current_app
from flask_pymongo import PyMongo
from pymongo import MongoClient

mongo = PyMongo()

ADMIN_DB = 'master_data_admin'


def get_db_connection(db_name):
    uri = current_app.config.get('MONGO_URI')
    connection = MongoClient(uri)
    return connection[db_name]
