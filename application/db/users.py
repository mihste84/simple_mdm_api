import datetime

from application.db import get_db_connection, ADMIN_DB


def get_user_by_email(email):
    db = get_db_connection(ADMIN_DB)
    return db.users.find_one({'email': email})


def create_new_user(username, email):
    db = get_db_connection(ADMIN_DB)
    now = datetime.datetime.utcnow()
    return db.users.insert_one({'username': username, 'email': email, 'created': now})
