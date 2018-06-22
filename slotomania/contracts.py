import pprint
from enum import Enum, auto
from typing import List, Union, ClassVar
from yapf.yapflib.yapf_api import FormatCode

TypeChoices = Union["PrimitiveValueType", "Contract", "ListField"]


def format_python_code(code: str, style_config='setup.cfg'):
    return FormatCode(f'{code}')[0]


class PrimitiveValueType(Enum):
    # Primitive
    STRING = auto()
    INTEGER = auto()
    DECIMAL = auto()
    FLOAT = auto()
    DATETIME = auto()

    def to_python_type(self) -> str:
        return {
            "STRING": 'str',
            "INTEGER": 'int',
            "DECIMAL": 'decimal.Decimal',
            "FLOAT": 'float',
            "DATETIME": 'datetime.datetime',
        }[self.name]

    def to_typescript(self) -> str:
        return {
            "STRING": 'string',
            "INTEGER": 'number',
            "DECIMAL": 'number',
            "FLOAT": 'number',
            "DATETIME": 'string',
        }[self.name]


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

    def __init__(
        self,
        name: str,
        value_type: Union[TypeChoices, List[TypeChoices]],
        required: bool = True,
    ) -> None:
        # assert isinstance(value_type,
        #                   PrimitiveValueType) or isinstance(value_type, list)
        self.name = name
        self.value_type = value_type
        self.required = required

    def to_python_type(self) -> str:
        if isinstance(self.value_type, list):
            return "typing.Union[{}]".format(
                ",".join([t.to_python_type() for t in self.value_type])
            )
        return self.value_type.to_python_type()

    def to_typescript(self) -> str:
        if isinstance(self.value_type, list):
            return "|".join([t.to_typescript() for t in self.value_type])
        return self.value_type.to_typescript()


class ListField(Field):
    def to_python_type(self) -> str:
        type_string = super().to_python_type()
        return f"typing.List[{type_string}]"

    def to_typescript(self) -> str:
        type_string = super().to_typescript()
        return f"Array<{type_string}>"


class Contract(Sloto):
    __slots__ = ["fields"]

    def __init__(
        self,
        name: str,
        fields: List[Field],
    ) -> None:
        assert name[0].isupper(
        ), f"Invalid contract name '{name}'. Must start with an upper case letter"
        self.name = name
        # Required args come first
        self.fields = sorted(fields, key=lambda f: (-f.required, f.name))

    def to_python_type(self) -> str:
        return self.name

    def to_typescript(self) -> str:
        return self.name

    def translate_to_typescript(self) -> str:
        interface_body = '\n'.join(
            [
                # field_name, optional, field_type
                f"  {field.name}: {field.to_typescript()}" if field.required
                else f"  {field.name}?: {field.to_typescript()}"
                for field in self.fields
            ]
        )
        return 'export interface {} {{\n{}\n}}'.format(
            self.name, interface_body
        )

    def translate_to_slots(self) -> str:
        init_args = ",\n        ".join(
            [
                f"{field.name}: {field.to_python_type()}" if field.required
                else f"{field.name}: {field.to_python_type()} = None"
                for field in self.fields
            ]
        )
        field_names = ', '.join(f"'{field.name}'" for field in self.fields)
        assignments = "\n        ".join(
            f"self.{field.name} = {field.name}" for field in self.fields
        )
        code = f"""
import datetime
import decimal
import typing

class {self.name}:
    __slots__ = [{field_names}]
    def __init__(
        self,
        {init_args},
        ) -> None:

        {assignments}
        """
        return format_python_code(code)
