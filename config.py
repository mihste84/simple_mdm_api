from decouple import config


class Config:
    def __init__(self):
        pass

    FLASK_ENV = config('FLASK_ENV')
    FLASK_APP = config('FLASK_APP')
    MONGO_URI = config('MONGO_URI')
    MSAL_AUDIENCE = config('MSAL_AUDIENCE')
    MSAL_DISCOVERY = config('MSAL_DISCOVERY')
