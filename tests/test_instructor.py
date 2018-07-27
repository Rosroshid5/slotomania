from unittest import TestCase

from slotomania.contrib.contracts import AuthenticateUserRequest
from slotomania.core import EntityTypes, Instruction, Operation


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
