class AirtableException(Exception):
    pass


class ShortPassword(AirtableException):
    pass


class IncorrectUser(AirtableException):
    pass


class IncorrectPassword(AirtableException):
    pass


class UsernameIsBusy(AirtableException):
    pass