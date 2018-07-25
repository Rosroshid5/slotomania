from dataclasses import dataclass
from slotomania.contractor import Contract


@dataclass
class AuthenticateUserRequest(Contract):
    username: str
    password: str


@dataclass
class EmptyBodySchema(Contract):
    pass
