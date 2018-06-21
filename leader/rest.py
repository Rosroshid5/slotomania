# import typing
#
# from django.template import engines
# from django.core.exceptions import PermissionDenied
# from rest_framework import serializers
#
# from .utils import drf_field_to_dict, drf_field_to_ts, drf_field_to_python
#
# django_engine = engines['django']
#
#
# def serializer_to_python_namedtuple(serializer_class) -> str:
#     fields = serializer_class().get_fields()
#     body = '\n'.join(drf_field_to_python(name, field)
#                      for name, field in fields.items())
#     return 'class {}(typing.NamedTuple):\n    {}'.format(serializer_class.__name__, body)
#
#
# def serializer_to_ts_interface(serializer_class: serializers.Serializer) -> str:
#     """Give a serializer class, convert it to typescript interface."""
#     fields = serializer_class().get_fields()
#     body = '\n'.join(drf_field_to_ts(name, field)
#                      for name, field in fields.items())
#     return 'export interface {} {{\n{}\n}}'.format(serializer_class.__name__, body)
#
#
# class CommandInterface(serializers.Serializer):
#
#     @classmethod
#     def to_ts(cls) -> str:
#         """Used for function signatures such as func(x: string)."""
#         fields = cls().get_fields()
#         return '\n'.join(drf_field_to_ts(name, field)
#                          for name, field in fields.items())
#
#     @classmethod
#     def as_json(cls) -> typing.List[dict]:
#         return [
#             {'name': name, **drf_field_to_dict(field)}
#             for name, field in cls().get_fields().items()
#         ]
