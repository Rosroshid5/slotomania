# from unittest import TestCase
# from marshmallow import Schema, fields
#
# from yapf.yapflib.yapf_api import FormatCode
#
# from ..translator import (
#     translate_to_python_field,
#     translate_to_python_slot,
#     translate_to_typescript_field,
#     translate_to_typescript_interface,
#     fields_to_ts_redux_action,
#     translate_to_python_module,
# )
#
#
# class Deep:
#     one = fields.Str(required=True)
#     two = fields.Int(required=True)
#
#     def get_fields(self):
#         return {'one': self.one, 'two': self.two}
#
#
# class Baby(Schema):
#     name = fields.Str(required=True)
#     age = fields.Int(required=True)
#
#
# class Parent(Schema):
#     id = fields.Int(required=True)
#     notes = fields.Str(required=True)
#     not_required = fields.Int(required=False)
#     is_ignored = fields.Bool(required=False)
#     boy = fields.Nested(Baby(), required=True)
#
#
# class TranslatorTestCase(TestCase):
#     def test_translate_to_python_field(self):
#
#         assert translate_to_python_field(fields.Int()) == 'int'
#         assert translate_to_python_field(fields.Str()) == 'str'
#         assert translate_to_python_field(fields.List(fields.Str())) == 'typing.List[str]'
#         assert translate_to_python_field(fields.List(fields.Int())) == 'typing.List[int]'
#
#         assert translate_to_python_field(Deep()) == 'Deep'
#
#     def test_translate_to_typescript_field(self):
#         assert translate_to_typescript_field(fields.Int()) == 'number'
#         assert translate_to_typescript_field(fields.Str()) == 'string'
#         assert translate_to_typescript_field(fields.List(fields.Str())) == 'Array<string>'
#         assert translate_to_typescript_field(fields.List(fields.Int())) == 'Array<number>'
#
#         assert translate_to_typescript_field(Deep()) == 'Deep'
#
#     def test_translate_to_python_slot(self) -> None:
#         expected = FormatCode(
#             '''class Deep:
#             __slots__ = ['one', 'two']
#             def __init__(self, one: str, two: int) -> None:
#                 self.one = one
#                 self.two = two
#             '''
#         )[0]
#         assert translate_to_python_slot('Deep', Deep().get_fields()) == expected
#
#     def test_fields_to_ts_redux_action(self) -> None:
#         assert fields_to_ts_redux_action('MyAction',
#                                          Deep().get_fields()) == '''
#     export function MyAction(command_context: { one: string
# two: number } ): any {
#         return (dispatch) => {
#             return dispatch(
#                 sendCommand("MyAction", command_context, )
#             )
#         }
#     }'''
#
#     def test_fields_to_ts_interface(self) -> None:
#         assert translate_to_typescript_interface('Parent',
#                                                  Parent().fields) == """export interface Parent {
# boy: Baby
# id: number
# is_ignored?: boolean
# not_required?: number
# notes: string
# }"""
#
#     def test_generate_python_module_with_custom_base_class(self) -> None:
#         assert translate_to_python_module(
#             [('Baby', Baby().fields)], base_class='mymod.MyBaseClass'
#         ) == FormatCode(
#             """
# import typing
# import decimal
# import datetime
# import mymod
#
# class Baby(mymod.MyBaseClass):
#     __slots__ = ['age', 'name']
#     def __init__(self, age: int, name: str) -> None:
#         self.age = age
#         self.name = name
#
#         """
#         )[0]
