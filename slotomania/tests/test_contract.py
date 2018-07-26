from dataclasses import asdict, dataclass, is_dataclass
import datetime
from typing import List, Optional
from unittest import TestCase

from slotomania.core import Contract, ReduxAction, contracts_to_typescript


@dataclass
class Address(Contract):
    street: str


@dataclass
class Person(Contract):
    name: str
    gender: bool
    birth_date: datetime.datetime
    addresses: Optional[List[Address]] = None


class DataclassConverterTestCase(TestCase):
    def test_dataclass_converter(self) -> None:
        assert is_dataclass(Person)
        man = Person(
            "Bond", True, datetime.datetime.utcnow(), [Address("easy street")]
        )
        woman = Person("Girl", True, datetime.datetime.utcnow())
        assert is_dataclass(man) and is_dataclass(woman)
        assert contracts_to_typescript(
            dataclasses=[Person],
            redux_actions=[ReduxAction(name="CreatePerson", contract=Person)],
            import_plugins=False,
        ) == """export interface Person {
  name: string
  gender: boolean
  birth_date: string
  addresses?: Array<Address>|null
}

export function CreatePerson(requestBody: Person): any {
        return (dispatch) => {
            return dispatch(
                plugins.callEndpoint("CreatePerson", requestBody, )
            )
        }
    }

export const SLOTO_ACTION_CREATORS = { CreatePerson }"""

        assert man == man.load_from_dict(asdict(man))
