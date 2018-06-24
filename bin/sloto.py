#!/usr/bin/env python
import importlib
import argparse

from marshmallow import Schema
from slotomania.contrib.marshmallow_converter import schemas_to_slots

parser = argparse.ArgumentParser(
    description='Convert marshallow schemas to Python sloto classes '
    'and typescript interfaces.'
)
parser.add_argument(
    'schema_modules',
    type=str,
    nargs='*',
    help='Dotted path to the module containing marshmallow schemas.'
)
args = parser.parse_args()
for module in args.schema_modules:
    importlib.import_module(module)

schemas = Schema.__subclasses__()
assert len(schemas), "No schemas"

print(schemas_to_slots([schema() for schema in schemas]))
