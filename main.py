import argplusplus as argpp
from argplusplus.parser import _class, flag

parser = _class.Parser()
parser.add(
    flag.Command(("example", "one"), arguments=(flag.Argument("x"),))
)
print(parser.process())