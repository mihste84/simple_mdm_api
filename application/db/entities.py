import uuid
from datetime import datetime

from bson import ObjectId

from application.db import get_db_connection, ADMIN_DB


def get_entity_by_prop(name, value, model_id=None):
    db = get_db_connection(ADMIN_DB)
    match = {f'entities.{name}': value, '_id': ObjectId(model_id)} if model_id else {f'entities.{name}': value}
    return db.models.aggregate([
        {'$match': match},
        {'$project': {
            'entities': {
                '$filter': {
                    'input': '$entities',
                    'as': 'entity',
                    'cond': {'$eq': [f'$$entity.{name}', value]}
                }
            }
        }},
        {
            '$project': {
                'entities': {
                    '$map': {
                        'input': '$entities',
                        'as': 'entity',
                        'in': {
                            'name': '$$entity.name',
                            'id': '$$entity.id',
                            'updatedBy': '$$entity.updatedBy',
                            'updated': {'$dateToString': {'date': '$$entity.updated'}},
                            'description': '$$entity.description',
                            'isActive': '$$entity.isActive',
                            'attributes': '$$entity.attributes',
                        }
                    }
                }
            }
        }
    ])


def delete_entity_by_id(entity_id):
    db = get_db_connection(ADMIN_DB)
    return db.models.update(
        {},
        {
            '$pull': {
                'entities': {
                    'id': entity_id
                }
            }
        }
    )


def create_new_entity(model_id, name, description, is_active, email):
    db = get_db_connection(ADMIN_DB)
    now = datetime.utcnow()
    entity_id = str(uuid.uuid4())
    res = db.models.update(
        {'_id': ObjectId(model_id)},
        {
            '$push': {
                'entities': {
                    '$each': [{
                        'id': entity_id,
                        'name': name,
                        'description': description,
                        'isActive': is_active,
                        'updatedBy': email,
                        'updated': now,
                        'createdBy': email,
                        'created': now,
                        'attributes': []
                    }]
                }
            }
        }
    )
    res['id'] = entity_id
    return res


def update_entity(entity_id, name, description, is_active, email):
    db = get_db_connection(ADMIN_DB)
    now = datetime.utcnow()

    return db.models.update_one(
        {},
        {
            '$set': {
                'entities.$[entity].name': name,
                'entities.$[entity].description': description,
                'entities.$[entity].isActive': is_active,
                'entities.$[entity].updatedBy': email,
                'entities.$[entity].updated': now,
            }
        },
        upsert=False,
        array_filters=[
            {
                'entity.id': {'$eq': entity_id}
            }
        ]
    )
