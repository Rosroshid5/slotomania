from typing import ClassVar, Callable, Type

from marshmallow import Schema, class_registry
from slotomania.core import Sloto


class RequestResolver:
    # data: MyDataType
    resolve: Callable
    pre_action: ClassVar[str] = ""
    callback: ClassVar[str] = ""

    def __init__(self, request, data: dict) -> None:
        self.request = request
        self._data = data
        sloto_klass = self.get_data_type()
        self.data = sloto_klass.sloto_from_dict(self.validate())

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if hasattr(cls, "resolve"):
            assert cls.__annotations__.get(
                "data"
            ), f"{cls} cannot define 'resovle' without annotating 'data'"

    def validate(self) -> dict:
        schema = self.get_schema()
        self.validate_data = schema.load(self.request.data)
        return self.validate_data

    @classmethod
    def get_data_type(cls) -> Type[Sloto]:
        return cls.__annotations__["data"]

    @classmethod
    def get_schema(cls) -> Schema:
        return class_registry.get_class(cls.get_data_type().__name__)()
