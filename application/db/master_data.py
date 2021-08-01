from datetime import datetime

from bson import ObjectId

from application.db import get_db_connection, ADMIN_DB


def get_model_admins_by_id(model_id):
    db = get_db_connection(ADMIN_DB)
    return db.models.find_one(
        {'_id': ObjectId(model_id)},
        {'admins': 1}
    )


def get_models_by_user_email(user_email):
    db = get_db_connection(ADMIN_DB)

    return db.models.aggregate(
        [
            {'$match': {'admins': {'$all': [user_email]}}},
            {'$project': {
                'name': 1,
                'createdBy': 1,
                'created': {'$dateToString': {'date': '$created'}},
                'isActive': 1,
                'admins': {'$size': '$admins'},
                'entities': {'$size': '$entities'}}}
        ]
    )


def get_model_by_id(model_id):
    db = get_db_connection(ADMIN_DB)
    entities = {
        '$map': {
            'input': '$entities',
            'as': 'entity',
            'in': {
                'name': '$$entity.name',
                'id': '$$entity.id',
                'createdBy': '$$entity.createdBy',
                'created': {'$dateToString': {'date': '$$entity.created'}},
                'description': '$$entity.description',
                'isActive': '$$entity.isActive',
                'attributes': {
                    '$sum':
                    {
                        '$map': {
                            'input': '$entities',
                            'in': {'$size': '$$this.attributes'}
                        }
                    }
                }
            }
        }
    }

    return db.models.aggregate(
        [
            {'$match': {'_id': ObjectId(model_id)}},
            {'$project': {
                'description': 1,
                'name': 1,
                'updatedBy': 1,
                'updated': {'$dateToString': {'date': '$updated'}},
                'createdBy': 1,
                'created': {'$dateToString': {'date': '$created'}},
                'isActive': 1,
                'admins': 1,
                'entities': entities}}
        ]
    )


def update_model(model_id, name, description, is_active, email):
    db = get_db_connection(ADMIN_DB)
    return db.models.update_one(
        {'_id': ObjectId(model_id)},
        {
            '$set': {
                'name': name,
                'description': description,
                'isActive': is_active,
                'updatedBy': email,
                'updated': datetime.utcnow()
            }
        }
    )


def create_new_model(name, description, is_active, email):
    db = get_db_connection(ADMIN_DB)
    now = datetime.utcnow()
    return db.models.insert_one(
        {
            'name': name,
            'description': description,
            'isActive': is_active,
            'updatedBy': email,
            'updated': now,
            'createdBy': email,
            'created': now,
            'admins': [email],
            'entities': []
        }
    )


def delete_model_by_id(model_id):
    db = get_db_connection(ADMIN_DB)
    return db.models.delete_one({'_id': ObjectId(model_id)})


def add_new_admin(model_id, admin):
    db = get_db_connection(ADMIN_DB)
    return db.models.update(
        {'_id': ObjectId(model_id)},
        {
            '$push': {
                'admins': admin
            }
        }
    )


def delete_admin(model_id, admin):
    db = get_db_connection(ADMIN_DB)
    return db.models.update(
        {'_id': ObjectId(model_id)},
        {
            '$pull': {
                'admins': admin
            }
        }
    )
