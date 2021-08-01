class NotFoundError(Exception):
    def __init__(self, msg=''):
        super.__init__(msg)


class DbOperationError(Exception):
    def __init__(self, msg=''):
        super.__init__(msg)


class BadRequest(Exception):
    def __init__(self, msg=''):
        super.__init__(msg)