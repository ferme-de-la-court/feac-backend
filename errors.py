class FarmerException(Exception):
    pass

class RestException(FarmerException):

    def __init__(self, message, code=400):
        super(RestException, self).__init__(message)
        self.code = code


class AuthException(RestException):

    def __init__(self, message):
        super().__init__(message, code=401)


class BadDataException(RestException):

    def __init__(self, message):
        super().__init__(message, code=400)


class NotFoundException(RestException):

    def __init__(self, message):
        super().__init__(message, code=404)
