#!/usr/bin/env python
import importlib
import argparse

from marshmallow import Schema
from slotomania.contrib.marshmallow_converter import (
    schemas_to_slots, schemas_to_typescript, RequestBodySchema
)

parser = argparse.ArgumentParser(
    description='Convert marshallow schemas to Python sloto classes '
    'and typescript interfaces.'
)
parser.add_argument(
    'language',
    type=str,
    nargs=1,
    choices=['python', 'typescript'],
    help='Output language. python or typescript'
)

parser.add_argument(
    'schema_modules',
    type=str,
    nargs='*',
    help='Dotted path to the module containing marshmallow schemas.'
)
parser.add_argument(
    '-o', '--outputfile', type=str, nargs='?', help='Outputfile'
)


def main():
    args = parser.parse_args()
    for module in args.schema_modules:
        importlib.import_module(module)

    schemas = [
        Klass() for Klass in
        (Schema.__subclasses__() + RequestBodySchema.__subclasses__())
        if Klass is not RequestBodySchema
    ]
    assert len(schemas), "No schemas"

    if args.language == ['python']:
        output = schemas_to_slots([schema for schema in schemas])
    else:
        output = schemas_to_typescript([schema for schema in schemas])

    if not args.outputfile:
        print(output)
    else:
        with open(args.outputfile, 'w') as f:
            print(output, file=f)


if __name__ == '__main__':
    main()
