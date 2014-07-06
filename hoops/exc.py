

class APIException(Exception):

    def __init__(self, status):
        self.status = status

    def get_dict(self):
        return self.status.get_dict()

    def __getattr__(self, name):
        return getattr(self.status, name)


class APIValidationException(APIException):

    def __init__(self, status, validation_errors):
        super(APIValidationException, self).__init__(status)
        self.extra = {"validation_errors": validation_errors}
