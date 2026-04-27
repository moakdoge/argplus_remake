import linecache
import traceback
class ParsingException(Exception):
    def __init__(self, *args: object) -> None:
        processed = []
        for arg in args:
            if hasattr(arg, "__traceback__") and isinstance(arg, Exception):
                tb = arg.__traceback__
                if tb is None:
                    continue
                while tb.tb_next:  # walk to the last frame (where it blew up)
                    tb = tb.tb_next
                line_no = tb.tb_lineno
                filename = tb.tb_frame.f_code.co_filename
                func_name = tb.tb_frame.f_code.co_name

                #get a couple of lines

                buffer = 3
                lines = []
                lines.append(linecache.getline(filename, line_no).strip())
                lines = ["\t" + l+" <<< HERE"for l in lines]
                processed.append(f"{type(arg).__name__} '{str(arg)}' raised at {func_name} @ Line {line_no}: \n{"\n".join(lines)}")
                continue
            processed.append(str(arg))
        super().__init__("error: "+" ".join(processed))

class MissingArgument(ParsingException):
    pass

class InvalidArgumentType(ParsingException):
    pass

class InvalidCommmand(ParsingException):
    pass

class InvalidArgument(ParsingException):
    pass