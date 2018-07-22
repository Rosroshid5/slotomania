from slotomania.contrib.schemas import RequestBodySchema, Schema
from slotomania.contrib.marshmallow_converter import schemas_to_slots


def main() -> None:
    python_output_file = 'slotomania/contrib/slots.py'

    schemas = [
        Klass() for Klass in Schema.__subclasses__() +
        RequestBodySchema.__subclasses__() if Klass is not RequestBodySchema
    ]
    python_code = schemas_to_slots(schemas)
    with open(python_output_file, 'w') as f:
        f.write(python_code)


if __name__ == '__main__':
    main()
