from slotomania.core import Sloto
import datetime
import decimal
import typing


class AuthenticateUserRequest(Sloto):
    __slots__ = ['password', 'username']

    def __init__(
            self,
            password: str,
            username: str,
    ) -> None:

        self.password = password
        self.username = username


class EmptyBodySchema(Sloto):
    __slots__ = []

    def __init__(self, ) -> None:

        pass
