[![codecov](https://codecov.io/gh/conanfanli/slotomania/branch/master/graph/badge.svg)](https://codecov.io/gh/conanfanli/slotomania)
![pyup](https://pyup.io/repos/github/conanfanli/slotomania/shield.svg)

Slotomania
================
A code generator that transforms schemas to Python slot classes and typescript interfaces

Examples
========

```Python
from slotomania.contrib.marshmallow_converter import (
    schemas_to_slots,
)
class Eye(Schema):
    color = fields.String(required=True)


class Head(Schema):
    hair = fields.String(requried=True)


class Body(Schema):
    eyes = fields.List(fields.Nested(Eye()), required=True)
    mouth = fields.Decimal(required=True)
    poo = fields.Float(required=True)
    foot = fields.DateTime(required=True)
    head = fields.Nested(Head(), required=True)

assert format_python_code(schemas_to_slots([
    Eye(),
    Head(),
    Body(),
])) == format_python_code("""
from slotomania.core import Sloto
import datetime
import decimal
import typing

class Eye(Sloto):
    __slots__ = ['color']
    def __init__(
        self,
        color: str,
    ) -> None:

        self.color = color


class Head(Sloto):
    __slots__ = ['hair']
    def __init__(
        self,
        hair: str = None,
    ) -> None:

        self.hair = hair


class Body(Sloto):
    __slots__ = ['eyes', 'foot', 'head', 'mouth', 'poo']
    def __init__(
        self,
        eyes: typing.List[Eye],
        foot: datetime.datetime,
        head: Head,
        mouth: decimal.Decimal,
        poo: float,
    ) -> None:

        self.eyes = eyes
        self.foot = foot
        self.head = head
        self.mouth = mouth
        self.poo = poo
        """
        )
```
