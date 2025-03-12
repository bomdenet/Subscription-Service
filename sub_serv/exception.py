class AirtableException(Exception):
    pass


class ShortPassword(AirtableException):
    pass


class ShortUsername(AirtableException):
    pass


class IncorrectCharectersInUsername(AirtableException):
    pass


class IncorrectCharectersInPassword(AirtableException):
    pass


class IncorrectUser(AirtableException):
    pass


class IncorrectPassword(AirtableException):
    pass


class UsernameIsBusy(AirtableException):
    pass