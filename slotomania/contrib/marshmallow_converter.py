from typing import List, Dict, ClassVar

from marshmallow import Schema, fields
from slotomania.core import (
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


class RequestBodySchema(Schema):
    redux_creator_function_name: ClassVar[str]

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        if not cls.redux_creator_function_name:
            raise AssertionError(
                f"{cls} need to define redux_creator_function_name"
            )


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


def schemas_to_typescript(schemas: List[Schema]) -> str:
    blocks = ['import * as slotoUtils from "./slotoUtils"']
    endpoints = {}
    for index, schema in enumerate(schemas):
        contract = schema_to_contract(schema)
        blocks.append(contract.translate_to_typescript())
        if isinstance(schema, RequestBodySchema):
            endpoints[schema.redux_creator_function_name] = schema

    if endpoints:
        blocks.append(get_redux_action_creators(endpoints))
        names = ',\n'.join(endpoints.keys())
        blocks.append(
            f"""export const SLOTO_ACTION_CREATORS = {{ {names} }}"""
        )

    return "\n\n".join(blocks)


def schemas_to_slots(schemas: List[Schema]) -> str:
    contracts = [schema_to_contract(schema) for schema in schemas]
    blocks = []
    for index, contract in enumerate(contracts):
        blocks.append(
            contract.translate_to_slots(include_imports=(index == 0))
        )

    return "\n\n".join(blocks)


def get_redux_action_creators(endpoints: Dict[str, Schema]) -> str:
    blocks = []
    for function_name, request_body_schema in endpoints.items():
        contract = schema_to_contract(request_body_schema)
        blocks.append(
            contract_to_redux_action_creator(
                contract=contract, function_name=function_name
            )
        )

    return "\n\n".join(blocks)


def contract_to_redux_action_creator(
    *,
    contract: Contract,
    function_name: str,
    callback='',
    pre_action='',
) -> str:
    return f"""export function {function_name}(requestBody: {contract.name}): any {{
    return (dispatch) => {{{pre_action}
        return dispatch(
            slotoUtils.callEndpoint("{function_name}", requestBody, {callback})
        )
    }}
}}"""
