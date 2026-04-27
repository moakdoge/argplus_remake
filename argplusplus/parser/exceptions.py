class ParsingException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__("error: "+" ".join([str(a) for a in args]))

class MissingArgument(ParsingException):
    pass

class InvalidArgumentType(ParsingException):
    pass

class InvalidCommmand(ParsingException):
    pass

class InvalidArgument(ParsingException):
    pass