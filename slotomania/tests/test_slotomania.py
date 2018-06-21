from slotomania.contracts import (
    Contract,
    PrimitiveField as PF,
    PrimitiveValueType as P,
    NestedField,
    ListField,
)

from unittest import TestCase


class SlotoTestCase(TestCase):
    def test_contract(self) -> None:
        head = Contract(fields=[PF("hair", P.STRING)])
        eye = Contract(fields=[PF("color", P.STRING)])
        contract = Contract(
            fields=[
                ListField("eyes", eye),
                PF("nose", P.INTEGER),
                PF("mouth", P.DECIMAL),
                PF("poo", P.FLOAT),
                PF("foot", P.DATETIME),
                NestedField("head", head),
            ]
        )
        print(contract)
        assert contract.translate_to_slots() == ""
        self.fail()
