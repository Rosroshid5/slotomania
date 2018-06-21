from slotomania.datatypes import Contract, Field

from unittest import TestCase


class SlotoTestCase(TestCase):
    def test_contract(self) -> None:
        contract = Contract(
            fields=[
                Field("eye", "STRING"),
                Field("nose", "INTEGER"),
                Field("mouth", "DICT"),
                Field("poo", "FLOAT"),
                Field("foot", "DECIMAL"),
            ]
        )
        print(contract)
        self.fail()
