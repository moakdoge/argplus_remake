class ParsingException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class MissingArgument(ParsingException):
    pass

class InvalidArgumentType(ParsingException):
    pass

class InvalidCommmand(ParsingException):
    pass

class InvalidArgument(ParsingException):
    pass