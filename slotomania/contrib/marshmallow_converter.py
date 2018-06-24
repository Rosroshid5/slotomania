from typing import List

from marshmallow import Schema, fields
from slotomania.contracts import (
    PrimitiveValueType,
    Contract,
    ListField,
    PrimitiveField,
    NestedField,
    SlotoField,
)

field_map = {
    fields.String: PrimitiveValueType.STRING,
    fields.Integer: PrimitiveValueType.INTEGER,
    fields.Decimal: PrimitiveValueType.DECIMAL,
    fields.Float: PrimitiveValueType.FLOAT,
    fields.DateTime: PrimitiveValueType.DATETIME,
}


def field_to_field(name: str, field) -> SlotoField:
    if type(field) in field_map:
        return PrimitiveField(
            name=name,
            value_type=field_map[type(field)],
            required=field.required
        )
    elif isinstance(field, fields.Nested):
        return NestedField(
            field.name,
            schema_to_contract(field.nested),
            required=field.required
        )
    elif isinstance(field, fields.List):
        return ListField(
            name,
            item_type=field_to_field(name, field.container),
            required=field.required
        )

    raise KeyError(f"{field} not found")


def schema_to_contract(schema: Schema) -> Contract:
    assert isinstance(schema, Schema), f"{schema} is not an instance of Schema"
    ret = []
    for name, field in schema.fields.items():
        ret.append(field_to_field(name, field))

    return Contract(schema.__class__.__name__, fields=ret)


def schemas_to_slots(schemas: List[Schema]) -> str:
    contracts = [schema_to_contract(schema) for schema in schemas]
    blocks = []
    for index, contract in enumerate(contracts):
        blocks.append(
            contract.translate_to_slots(include_imports=(index == 0))
        )

    return "\n".join(blocks)
