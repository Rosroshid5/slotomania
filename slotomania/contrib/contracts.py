from dataclasses import dataclass

from slotomania.core import Contract


@dataclass
class AuthenticateUserRequest(Contract):
    username: str
    password: str


@dataclass
class EmptyBodySchema(Contract):
    pass
