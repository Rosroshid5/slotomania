from enum import Enum
from typing import List, Tuple
from yapf.yapflib.yapf_api import FormatCode


class Language(Enum):
    PYTHON = 'PYTHON'
    TYPESCRIPT = 'TYPESCRIPT'


FIELD_MAPPING = {
    Language.PYTHON: {
        # marshmallow
        'DateTime': 'datetime.datetime',
        'String': 'str',
        'Boolean': 'bool',
        'Integer': 'int',
        'Decimal': 'decimal.Decimal',
        'Float': 'float',
        'Dict': 'dict',
        'List': lambda f: 'typing.List[{}]'.format(_get_field_type(f.container, Language.PYTHON)),
        'Nested': lambda f: '{}'.format(_get_field_type(f.nested, Language.PYTHON)),
    },
    Language.TYPESCRIPT: {
        # marshmallow
        'String': 'string',
        'Boolean': 'boolean',
        'Integer': 'number',
        'Decimal': 'string',
        'Float': 'string',
        'Dict': '{}',
        'List': lambda f: 'Array<{}>'.format(_get_field_type(f.container, Language.TYPESCRIPT)),
        'Nested': lambda f: '{}'.format(_get_field_type(f.nested, Language.TYPESCRIPT)),
    }
}


def translate_to_python_field(field) -> str:
    return _get_field_type(
        field,
        Language.PYTHON,
    )


def translate_to_typescript_field(field) -> str:
    return _get_field_type(field, Language.TYPESCRIPT)


def translate_to_typescript_interface(interface_name: str, fields_map: dict) -> str:
    interface_body = '\n'.join(
        [
            # field_name, optional, field_type
            '{0}{1}: {2}'
            .format(name, '' if getattr(field, 'required', True) else '?', translate_to_typescript_field(field))
            for name, field in sorted(fields_map.items())
        ]
    )
    return 'export interface {} {{\n{}\n}}'.format(interface_name, interface_body)


def translate_to_python_module(schemas: List[Tuple[str, dict]], base_class='') -> str:
    """Translate a list of schemas to a Python module."""
    classes = '\n'.join(
        translate_to_python_slot(class_name if not base_class else f'{class_name}({base_class})', fields_map)
        for class_name, fields_map in schemas
    )
    modules = ['typing', 'decimal', 'datetime']
    # If base_class is like some_module.some_file.SomeClass
    if len(base_class.split('.')) > 1:
        modules.append('.'.join(base_class.split('.')[:-1]))

    imports = '\nimport '.join(['', *modules])
    return format_python_code(f'{imports}\n{classes}')


def translate_to_python_slot(class_name: str, fields_map: dict) -> str:
    sorted_field_tuples = sorted(fields_map.items(), key=lambda t: (not getattr(t[1], 'required', True), t[0]))
    field_lines = ',\n        '.join(
        [
            '{0}: {1}{2}'.format(
                name, translate_to_python_field(field), '' if getattr(field, 'required', True) else ' = None'
            ) for name, field in sorted_field_tuples
        ]
    )
    field_names = ', '.join(sorted(f"'{name}'" for name in fields_map))
    assignments = '\n        '.join(f'self.{name} = {name}' for name, field in sorted_field_tuples)
    code = f'''
class {class_name}:
    __slots__ = [{field_names}]
    def __init__(
        self,
        {field_lines}
        ) -> None:
        {assignments}
    '''
    return format_python_code(code)


def fields_to_ts_redux_action(function_name: str, fields_map: dict, callback='', pre_action='') -> str:
    type_annotations = '\n'.join(
        [
            # field_name, optional, field_type
            '{0}{1}: {2}'
            .format(name, '' if getattr(field, 'required', True) else '?', translate_to_typescript_field(field))
            for name, field in sorted(fields_map.items())
        ]
    )
    return f'''
    export function {function_name}(command_context: {{ {type_annotations} }} ): any {{
        return (dispatch) => {{{pre_action}
            return dispatch(
                sendCommand("{function_name}", command_context, {callback})
            )
        }}
    }}'''


def format_python_code(code: str, style_config='setup.cfg'):
    return FormatCode(f'{code}')[0]


def _get_field_type(field, target_language: Language) -> str:
    field_class_name = field.__class__.__name__
    field_type = FIELD_MAPPING[target_language].get(field_class_name, None)
    if isinstance(field_type, str):
        return field_type
    elif callable(field_type):
        return field_type(field)
    else:
        return field_class_name


def translate_code(target_language: Language) -> str:
    pass
