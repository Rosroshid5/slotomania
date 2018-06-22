from slotomania.contracts import (
    Contract,
    Field,
    PrimitiveValueType as PVT,
    ListField,
    format_python_code,
)

from unittest import TestCase


class SlotoTestCase(TestCase):
    def test_contract_to_python(self) -> None:
        Head = Contract("Head", fields=[Field("hair", PVT.STRING)])
        Eye = Contract("Eye", fields=[Field("color", PVT.STRING)])
        Body = Contract(
            "Body",
            fields=[
                ListField("eyes", Eye),
                Field(
                    "nose", [
                        PVT.INTEGER,
                        Eye,
                        ListField("temp", Head),
                    ],
                    required=False
                ),
                Field("mouth", PVT.DECIMAL),
                Field("poo", PVT.FLOAT),
                Field("foot", PVT.DATETIME),
                Field("head", Head),
            ]
        )
        assert Body.translate_to_slots() == format_python_code(
            """
import datetime
import decimal
import typing

class Body:
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
        Head = Contract("Head", fields=[Field("hair", PVT.STRING)])
        Eye = Contract("Eye", fields=[Field("color", PVT.STRING)])
        Body = Contract(
            "Body",
            fields=[
                ListField("eyes", Eye),
                Field(
                    "nose", [
                        PVT.INTEGER,
                        Eye,
                        ListField("temp", Head),
                    ],
                    required=False
                ),
                Field("mouth", PVT.DECIMAL),
                Field("poo", PVT.FLOAT),
                Field("foot", PVT.DATETIME),
                Field("head", Head),
            ]
        )
        assert Body.translate_to_typescript() == (
            """export interface Body {
  eyes: Array<Eye>
  foot: string
  head: Head
  mouth: number
  poo: number
  nose?: number|Eye|Array<Head>
}"""
        )
