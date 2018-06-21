import pprint
from enum import Enum, auto
from typing import List, Union, ClassVar


class ValueType(Enum):
    STRING = auto()
    INTEGER = auto()
    DECIMAL = auto()
    FLOAT = auto()
    DICT = auto()


class Sloto:
    __slots__: List[str]

    def _sloto_to_dict(self) -> dict:
        ret = {}
        for field in self.__slots__:
            value = getattr(self, field)
            if hasattr(value, "_sloto_to_dict"):
                ret[field] = value._sloto_to_dict()
            else:
                ret[field] = value
        return ret

    def __repr__(self) -> str:
        return "{}({})".format(
            self.__class__.__name__, pprint.pformat(self._sloto_to_dict())
        )


class Field(Sloto):
    __slots__ = ["name", "value_type"]

    def __init__(self, name: str, value_type: Union[str, ValueType]) -> None:
        self.name = name
        self.value_type = ValueType[value_type] if isinstance(
            value_type, str
        ) else value_type


class Contract(Sloto):
    __slots__ = ["fields"]

    def __init__(self, fields: List[Field]) -> None:
        self.fields = fields
