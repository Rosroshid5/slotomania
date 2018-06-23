from typing import Union
from marshmallow import Schema, fields
from slotomania.contracts import PrimitiveValueType, Contract, ListField, PrimitiveField, UnionField, NestedField, SlotoField

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
        return NestedField(field.name, schema_to_contract(field.nested))
    # elif isinstance(field, Schema):
    #     return NestedField(name, schema_to_contract(field))
    elif isinstance(field, fields.List):
        return ListField(name, item_type=field_to_field(name, field.container))

    raise KeyError(f"{field} not found")


def schema_to_contract(schema: Schema) -> Contract:
    ret = []
    for name, field in schema.fields.items():
        ret.append(field_to_field(name, field))

    return Contract(schema.__class__.__name__, fields=ret)
