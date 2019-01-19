class MissingInformation(BaseException):
    def __init__(self, field_name):
        BaseException.__init__(self)
        self.message = "Missing field '%s'." % field_name


class InvalidInformation(BaseException):
    def __init__(self, field_name, reason):
        BaseException.__init__(self)
        self.message = "Field '%s' is invalid: '%s'" %(field_name, reason)
