from typing import List

from slotomania.core import (
    Contract,
    PrimitiveField,
    PrimitiveValueType as PVT,
    ListField,
    NestedField,
    UnionField,
    format_python_code,
    Sloto,
)

from unittest import TestCase


class Kid(Sloto):
    __slots__ = ["name"]

    def __init__(self, name: str) -> None:
        self.name = name


class Woman(Sloto):
    __slots__ = ["name", "shoes"]

    def __init__(self, name: str, shoes: List[str]) -> None:
        self.name = name
        self.shoes = shoes


class Man(Sloto):
    __slots__ = ["name", "wife", "kids", "extra"]

    def __init__(self, name: str, wife: Woman, kids: List[Kid],
                 extra: dict) -> None:
        self.name = name
        self.wife = wife
        self.kids = kids
        self.extra = extra


class SlotoTestCase(TestCase):
    def setUp(self):
        super().setUp()
        Head = Contract("Head", fields=[PrimitiveField("hair", PVT.STRING)])
        Eye = Contract("Eye", fields=[PrimitiveField("color", PVT.STRING)])
        self.Body = Contract(
            "Body",
            fields=[
                ListField("eyes", NestedField("eyes", Eye)),
                UnionField(
                    "nose",
                    value_types=[
                        PrimitiveField("", PVT.INTEGER),
                        NestedField("", Eye),
                        ListField("temp", NestedField("temp", Head)),
                    ],
                    required=False
                ),
                PrimitiveField("mouth", PVT.DECIMAL),
                PrimitiveField("poo", PVT.FLOAT),
                PrimitiveField("foot", PVT.DATETIME),
                NestedField("head", Head),
            ]
        )

    def test_nested_sloto_from_dict(self) -> None:
        data = {
            "name": "man",
            "extra": {
                "key": "value"
            },
            "wife": {
                "name": "woman",
                "shoes": ["green", "red"]
            },
            "kids": [{
                "name": "biggie"
            }, {
                "name": "tiny"
            }]
        }
        man = Man.sloto_from_dict(data)
        assert man.wife.name == "woman"
        assert man.wife.shoes == ["green", "red"]
        assert man.kids[0].name == "biggie"
        assert man.kids[1].name == "tiny"

        assert man.sloto_to_dict() == data

    def test_contract_to_python(self) -> None:
        assert self.Body.translate_to_slots(include_imports=True
                                            ) == format_python_code(
                                                """
from slotomania.core import Sloto
import datetime
import decimal
import typing

class Body(Sloto):
    __slots__ = ['eyes', 'foot', 'head', 'mouth', 'poo', 'nose']
    def __init__(
        self,
        eyes: typing.List[Eye],
        foot: datetime.datetime,
        head: Head,
        mouth: decimal.Decimal,
        poo: float,
        nose: typing.Union[int, Eye, typing.List[Head]] = None,
    ) -> None:

        self.eyes = eyes
        self.foot = foot
        self.head = head
        self.mouth = mouth
        self.poo = poo
        self.nose = nose
        """
                                            )

    def test_contract_to_type_script(self) -> None:
        assert self.Body.translate_to_typescript() == (
            """export interface Body {
  eyes: Array<Eye>
  foot: string
  head: Head
  mouth: number
  poo: number
  nose?: number|Eye|Array<Head>
}"""
        )
