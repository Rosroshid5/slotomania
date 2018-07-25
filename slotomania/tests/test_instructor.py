from unittest import TestCase
from slotomania.instructor import Instruction, Operation, EntityTypes
from slotomania.contrib.contracts import AuthenticateUserRequest


class InstructorTestCase(TestCase):
    def test_instruction_serialize(self) -> None:
        instruction = Instruction(
            [
                Operation.OVERWRITE(
                    EntityTypes.jwt_auth_token,
                    target_value=[AuthenticateUserRequest("user", "pass")]
                )
            ]
        )
        print(instruction.serialize())
        assert instruction.serialize() == {
            "errors":
            None,
            "redirect":
            "",
            "operations": [
                {
                    "verb": "OVERWRITE",
                    "entity_type": "jwt_auth_token",
                    "target_value": [{
                        "username": "user",
                        "password": "pass"
                    }],
                }
            ]
        }
