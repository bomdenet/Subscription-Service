class AirtableException(Exception):
    pass


class ShortUsername(AirtableException):
    pass


class ShortPassword(AirtableException):
    pass


class IncorrectCharectersInUsername(AirtableException):
    pass


class IncorrectCharectersInPassword(AirtableException):
    pass


class IncorrectUsername(AirtableException):
    pass


class IncorrectPassword(AirtableException):
    pass


class UsernameIsBusy(AirtableException):
    pass