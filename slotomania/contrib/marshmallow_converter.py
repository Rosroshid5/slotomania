from typing import List, NamedTuple

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
    fields.Boolean: PrimitiveValueType.BOOLEAN,
    fields.Dict: PrimitiveValueType.DICT,
}


class ReduxAction(NamedTuple):
    name: str
    schema: Schema
    pre_action: str = ""
    callback: str = ""


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


def schemas_to_typescript(
    *,
    interface_schemas: List[Schema],
    redux_actions: List[ReduxAction],
) -> str:
    """
    Args:
        interface_schemas: A list of schemas to be converted to typescript
    interfaces.
        redux_actions: A list of ReduxAction to be converted to typescript
    creators.
    """
    blocks = ['import * as instructor from "./instructor"']
    for index, schema in enumerate(interface_schemas):
        contract = schema_to_contract(schema)
        blocks.append(contract.translate_to_typescript())

    if redux_actions:
        blocks.append(write_redux_actions(redux_actions))
        names = ',\n'.join([action.name for action in redux_actions])
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


def write_redux_actions(redux_actions: List[ReduxAction]) -> str:
    blocks = []
    for redux_action in redux_actions:
        contract = schema_to_contract(redux_action.schema)
        blocks.append(
            contract_to_redux_action_creator(
                contract=contract,
                function_name=redux_action.name,
                pre_action=redux_action.pre_action,
                callback=redux_action.callback,
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
            instructor.callEndpoint("{function_name}", requestBody, {callback})
        )
    }}
}}"""
