from slotomania.contracts import (
    Contract, PrimitiveField as PF, PrimitiveValueType as P, NestedField
)

from unittest import TestCase


class SlotoTestCase(TestCase):
    def test_contract(self) -> None:
        head = Contract(fields=[PF("hair", P.STRING)])
        contract = Contract(
            fields=[
                PF("eye", P.STRING),
                PF("nose", P.INTEGER),
                PF("mouth", P.DECIMAL),
                PF("poo", P.FLOAT),
                PF("foot", P.DATETIME),
                NestedField("head", head),
            ]
        )
        print(contract)
        assert contract.translate_to_slots() == ''
        self.fail()
