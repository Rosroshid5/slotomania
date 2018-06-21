from slotomania.contracts import (
    Contract,
    PrimitiveField as PF,
    PrimitiveValueType as P,
    NestedField,
    ListField,
    format_python_code,
)

from unittest import TestCase


class SlotoTestCase(TestCase):
    def test_contract(self) -> None:
        head = Contract("Head", fields=[PF("hair", P.STRING)])
        eye = Contract("Eye", fields=[PF("color", P.STRING)])
        contract = Contract(
            "Body",
            fields=[
                ListField("eyes", NestedField("eye", eye)),
                PF("nose", P.INTEGER),
                PF("mouth", P.DECIMAL),
                PF("poo", P.FLOAT),
                PF("foot", P.DATETIME),
                NestedField("head", head),
            ]
        )
        assert contract.translate_to_slots() == format_python_code(
            """
import datetime
import decimal
import typing

class Body:
    __slots__ = ['eyes', 'nose', 'mouth', 'poo', 'foot', 'head']
    def __init__(
        self,
        eyes: typing.List[Eye],
        nose: int,
        mouth: decimal.Decimal,
        poo: float,
        foot: datetime.datetime,
        head: Head,
    ) -> None:

        self.eyes = eyes
        self.nose = nose
        self.mouth = mouth
        self.poo = poo
        self.foot = foot
        self.head = head
        """
        )
