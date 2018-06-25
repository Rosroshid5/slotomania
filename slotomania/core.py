import pprint
from enum import Enum, auto
from typing import List, Union
from yapf.yapflib.yapf_api import FormatCode


def format_python_code(code: str, style_config='setup.cfg') -> str:
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


class SlotoField(Sloto):
    required: bool
    name: str

    def to_python_type(self) -> str:
        raise NotImplementedError()

    def to_typescript(self) -> str:
        raise NotImplementedError()


class PrimitiveField(SlotoField):
    __slots__ = ["name", "value_type", "required"]

    def __init__(
        self,
        name: str,
        value_type: PrimitiveValueType,
        required: bool = True,
    ) -> None:
        assert isinstance(value_type, PrimitiveValueType)
        self.name = name
        self.value_type = value_type
        self.required = required

    def to_python_type(self) -> str:
        return self.value_type.to_python_type()

    def to_typescript(self) -> str:
        return self.value_type.to_typescript()


class NestedField(SlotoField):
    __slots__ = ["name", "nested_contract", "required"]

    def __init__(
        self,
        name: str,
        nested_contract: "Contract",
        required: bool = True,
    ) -> None:
        assert isinstance(
            nested_contract, Contract
        ), f"{nested_contract} is not a Contract"
        self.name = name
        self.nested_contract = nested_contract
        self.required = required

    def to_python_type(self) -> str:
        return self.nested_contract.to_python_type()

    def to_typescript(self) -> str:
        return self.nested_contract.to_typescript()


class UnionField(SlotoField):
    __slots__ = ["name", "value_types", "required"]

    def __init__(
        self,
        name: str,
        value_types: List[Union["ListField", PrimitiveField, NestedField]],
        required: bool = True,
    ) -> None:
        self.name = name
        self.value_types = value_types
        self.required = required

    def to_python_type(self) -> str:
        return "typing.Union[{}]".format(
            ",".join([t.to_python_type() for t in self.value_types])
        )

    def to_typescript(self) -> str:
        return "|".join([t.to_typescript() for t in self.value_types])


class ListField(SlotoField):
    __slots__ = ["name", "item_type", "required"]

    def __init__(
        self,
        name: str,
        item_type: SlotoField,
        required: bool = True,
    ) -> None:
        self.name = name
        self.item_type = item_type
        self.required = required

    def to_python_type(self) -> str:
        type_string = self.item_type.to_python_type()
        return f"typing.List[{type_string}]"

    def to_typescript(self) -> str:
        type_string = self.item_type.to_typescript()
        return f"Array<{type_string}>"


class Contract(Sloto):
    __slots__ = ["name", "fields"]

    def __init__(
        self,
        name: str,
        fields: List[SlotoField],
    ) -> None:
        assert name[0].isupper(
        ), f"Invalid contract name '{name}'. Start with an upper case letter!"
        self.name = name
        # Required args come first
        for field in fields:
            pass
            # assert isinstance(field, Field), field
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

    def translate_to_slots(
        self,
        include_imports: bool = False,
        # dotted path to the class
        base_class_path: str = 'slotomania.core.Sloto',
    ) -> str:
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
        default_imports = (
            "import datetime\nimport decimal\nimport typing\n\n"
        )
        if base_class_path != 'object':
            module_path, base_class = base_class_path.rsplit('.', maxsplit=1)
            imports = (
                f'from {module_path} import {base_class}\n' + default_imports
            )

        imports = imports if include_imports else ""
        code = f"""
{imports}
class {self.name}({base_class}):
    __slots__ = [{field_names}]
    def __init__(
        self,
        {init_args},
        ) -> None:

        {assignments}"""
        return format_python_code(code)
