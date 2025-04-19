class BaseDataException(Exception):
    pass


class ShortUsername(BaseDataException):
    pass


class ShortPassword(BaseDataException):
    pass


class IncorrectCharectersInUsername(BaseDataException):
    pass


class IncorrectCharectersInPassword(BaseDataException):
    pass


class IncorrectUsername(BaseDataException):
    pass


class IncorrectPassword(BaseDataException):
    pass


class UsernameIsBusy(BaseDataException):
    pass


class UserHasNoRights(BaseDataException):
    pass


class NameIsBusy(BaseDataException):
    pass


class IncorrectName(BaseDataException):
    pass


class IncorrectDiscount(BaseDataException):
    pass


class IncorrectSubscription(BaseDataException):
    pass