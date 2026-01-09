import re
from enum import Enum

from astronverse.actionlib.types import Bool, List, Dict, Any


class CondType(Enum):
    C_TRUE = "true"
    C_FALSE = "false"
    C_EMPTY = "empty"
    C_NOT_EMPTY = "notempty"
    C_GT = ">"
    C_LT = "<"
    C_GE = ">="
    C_LE = "<="
    C_IN = "in"
    C_NOT_IN = "notin"
    C_EQ = "=="
    C_NE = "!="


def str_is_integer(s):
    return bool(re.match(r"^-?\d+$", s))


def str_is_float(s):
    return bool(re.match(r"^-?\d*\.\d+$", s))


def str_is_list(s):
    return bool(s.startswith("[") and s.endswith("]"))


def str_is_dict(s):
    return bool(s.startswith("{") and s.endswith("}"))


def consequence(args1: Any, condition: str, args2: Any = None, **kwargs):
    match condition:
        case CondType.C_TRUE.value | CondType.C_FALSE.value:
            res = bool(Bool.__validate__("arg1", args1))
            if condition == CondType.C_TRUE.value:
                return res
            else:
                return not res
        case CondType.C_EMPTY.value | CondType.C_NOT_EMPTY.value:
            if args1 is None:
                res = True
            elif isinstance(args1, str):
                res = not bool(args1.strip())
            else:
                res = False
            if condition == CondType.C_EMPTY.value:
                return res
            else:
                return not res
        case CondType.C_GT.value | CondType.C_LT.value | CondType.C_GE.value | CondType.C_LE.value:
            if isinstance(args1, str) and (str_is_integer(args1) or str_is_float(args1)):
                if str_is_integer(args1):
                    args1 = int(args1)
                else:
                    args1 = float(args1)
            elif isinstance(args1, float) or isinstance(args1, int):
                pass
            else:
                args1 = str(args1)

            if isinstance(args2, str) and (str_is_integer(args2) or str_is_float(args2)):
                if str_is_integer(args2):
                    args2 = int(args2)
                else:
                    args2 = float(args2)
            elif isinstance(args2, float) or isinstance(args2, int):
                pass
            else:
                args2 = str(args2)

            if condition == CondType.C_GT.value:
                return args1 > args2
            elif condition == CondType.C_LT.value:
                return args1 < args2
            elif condition == CondType.C_GE.value:
                return args1 >= args2
            elif condition == CondType.C_LE.value:
                return args1 <= args2
        case CondType.C_EQ.value | CondType.C_NE.value:
            args1_t = type(args1)
            args2_t = type(args2)
            if args1_t == args2_t:
                pass
            else:
                args1 = str(args1)
                args2 = str(args2)

            res = args1 == args2
            if condition == CondType.C_EQ.value:
                return res
            else:
                return not res
        case CondType.C_IN.value | CondType.C_NOT_IN.value:
            if isinstance(args1, str) and str_is_list(args1):
                args1 = list(List.__validate__("args1", args1))
            elif isinstance(args1, str) and str_is_dict(args1):
                args1 = dict(Dict.__validate__("args1", args1))
            else:
                pass

            if isinstance(args1, list):
                args1 = [str(x) for x in args1]

            if str(args2) in args1:
                res = True
            else:
                res = False

            if condition == CondType.C_IN.value:
                return res
            else:
                return not res
        case _:
            return False
