import datetime
from decimal import Decimal
from typing import List, TypeVar, Type, Dict, Union, ForwardRef  # type:ignore
from dataclasses import dataclass, Field, MISSING, is_dataclass, asdict
from slotomania.exceptions import MissingField


def is_field_required(field: Field) -> bool:
    return field.default is MISSING


TYPE_MAP = {
    str: 'string',
    bool: 'boolean',
    int: 'number',
    Decimal: 'string',
    float: 'number',
    datetime.datetime: 'string',
    dict: '{}',
}


def python_type_to_typescript(python_type: type) -> str:
    if python_type in TYPE_MAP:
        return TYPE_MAP[python_type]

    if is_dataclass(python_type):
        return python_type.__name__

    if getattr(python_type, "__name__", None) == "NoneType":
        return "null"

    if getattr(python_type, "__origin__", None) == list:
        args = getattr(python_type, "__args__")
        return "Array<{}>".format(python_type_to_typescript(args[0]))

    if getattr(python_type, "__origin__", None) == Union:
        args = getattr(python_type, "__args__")
        return "|".join(python_type_to_typescript(arg) for arg in args)

    if isinstance(python_type, ForwardRef):
        return python_type.__forward_arg__

    raise Exception(f"Unknow type {python_type}")


def field_to_typescript(field: Field) -> str:
    return python_type_to_typescript(field.type)


T = TypeVar("T", bound="Contract")


@dataclass
class Contract:
    def asdict(self) -> dict:
        return asdict(self)

    @classmethod
    def get_fields(cls: Type["Contract"]) -> Dict[str, Field]:
        return getattr(cls, "__dataclass_fields__")

    @classmethod
    def translate_to_typescript(cls: Type["Contract"]) -> str:
        interface_body = '\n'.join(
            [
                f"  {field.name}: {field_to_typescript(field)}"
                if is_field_required(field) else
                f"  {field.name}?: {field_to_typescript(field)}"
                for name, field in cls.get_fields().items()
            ]
        )
        return 'export interface {} {{\n{}\n}}'.format(
            cls.__name__, interface_body
        )

    @classmethod
    def load_from_dict(cls: Type[T], data: dict) -> T:
        kwargs = {}
        annotation = cls.__init__.__annotations__
        PRIMITIVES = list(TYPE_MAP.keys())

        def convert_value(value, value_type):
            if value_type in PRIMITIVES:
                return value
            elif is_dataclass(value_type):
                return value_type.load_from_dict(value)
            elif getattr(value_type, "__origin__", None) == Union:
                args = getattr(value_type, "__args__")
                # TODO: natively chose first type in Union
                return convert_value(value, args[0])
            elif value_type.__origin__ == list:
                # e.g. List[OtherSloto]
                nested_type = value_type.__args__[0]
                return [convert_value(item, nested_type) for item in value]
            else:
                raise Exception(
                    f"not sure what to do with {value_type}: {value}"
                )

        for key in data:
            if key in cls.get_fields():
                arg_type = annotation[key]
                kwargs[key] = convert_value(data[key], arg_type)

        for name, field in cls.get_fields().items():
            if is_field_required(field) and name not in data:
                raise MissingField(field)

        return cls(**kwargs)  # type: ignore


@dataclass
class ReduxAction:
    name: str
    contract: Contract
    pre_action: str = ""
    callback: str = ""


def contracts_to_typescript(
    *,
    dataclasses: List[Type[Contract]],
    redux_actions: List[ReduxAction],
    import_plugins: bool = True,
) -> str:
    """
    Args:
        interface_schemas: A list of schemas to be converted to typescript
    interfaces.
        redux_actions: A list of ReduxAction to be converted to typescript
    creators.
    """
    blocks = import_plugins and ['import * as instructor from "./instructor"'
                                 ] or []
    for index, contract in enumerate(dataclasses):
        blocks.append(contract.translate_to_typescript())

    if redux_actions:
        # blocks.append(write_redux_actions(redux_actions))
        names = ',\n'.join([action.name for action in redux_actions])
        blocks.append(
            f"""export const SLOTO_ACTION_CREATORS = {{ {names} }}"""
        )

    return "\n\n".join(blocks)
