import pprint
from enum import Enum, auto
from typing import List, Union, ClassVar

FieldTypes = Union["PrimitiveField", "NestedField", "ListField"]


class PrimitiveValueType(Enum):
    # Primitive
    STRING = auto()
    INTEGER = auto()
    DECIMAL = auto()
    FLOAT = auto()
    DATETIME = auto()
    # Nested
    # DICT = auto()
    # LIST = auto()

    # Language.PYTHON: {
    #     # marshmallow
    #     'DateTime': 'datetime.datetime',
    #     'String': 'str',
    #     'Boolean': 'bool',
    #     'Integer': 'int',
    #     'Decimal': 'decimal.Decimal',
    #     'Float': 'float',
    #     'Dict': 'dict',
    #     'List': lambda f: 'typing.List[{}]'.format(_get_field_type(f.container, Language.PYTHON)),
    #     'Nested': lambda f: '{}'.format(_get_field_type(f.nested, Language.PYTHON)),
    # },


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


class PrimitiveField(Sloto):
    __slots__ = ["name", "value_type"]

    def __init__(self, name: str, value_type: PrimitiveValueType) -> None:
        self.name = name
        self.value_type = value_type


class NestedField(Sloto):
    __slots__ = ["name", "sub_contract"]

    def __init__(self, name: str, sub_contract: "Contract") -> None:
        self.name = name
        self.sub_contract = sub_contract


class ListField(Sloto):
    __slots__ = ["name", "item_type"]

    def __init__(
        self,
        name: str,
        item_type: Union["Contract", PrimitiveValueType],
    ) -> None:
        self.name = name
        self.item_type = item_type


class Contract(Sloto):
    __slots__ = ["fields"]

    def __init__(
        self,
        fields: List[FieldTypes],
    ) -> None:
        self.fields = fields
