import json
from enum import auto, Enum
from typing import Type, Dict, Any, Union, NamedTuple, List

from django.db import transaction
from django.http import HttpResponse
from django.http import JsonResponse
from django.views import View

from slotomania.contrib.request_resolver import RequestResolver


class InstructorView(View):
    permission_classes: list = []
    routes: Dict[str, Type[RequestResolver]]

    def get(self, request: Any, endpoint: str = None) -> JsonResponse:
        return JsonResponse({})

    @transaction.atomic
    def post(
        self, request: Any, endpoint: str, *args, **kwargs
    ) -> JsonResponse:
        """If mustate_state returns HttpResponse, return it."""
        request.data = json.loads(request.body)
        resolver = self.routes[endpoint](request=request, data=request.data)
        response = resolver.resolve()
        if isinstance(response, HttpResponse):
            return response
        elif hasattr(response, "sloto_to_dict"):
            return JsonResponse(response.sloto_to_dict())
        elif isinstance(response, dict):
            return JsonResponse(response)
        elif hasattr(response, 'serialize'):
            return JsonResponse(response.serialize())
        else:
            raise AssertionError('Unknow type: {}'.format(type(response)))


class Verbs(Enum):
    DELETE = auto()
    MERGE_APPEND = auto()
    MERGE_PREPEND = auto()
    OVERWRITE = auto()


class Operation(NamedTuple):
    verb: Verbs
    entity_type: Enum
    target_value: Union[list, dict]

    @classmethod
    def MERGE_APPEND(cls, entity_type: Enum, target_value) -> 'Operation':
        assert isinstance(
            target_value, list
        ), f"'{target_value}' is not a list"
        return Operation(Verbs.MERGE_APPEND, entity_type, target_value)

    @classmethod
    def MERGE_PREPEND(cls, entity_type: Enum, target_value) -> 'Operation':
        assert isinstance(
            target_value, list
        ), f"'{target_value}' is not a list"
        return Operation(Verbs.MERGE_PREPEND, entity_type, target_value)

    @classmethod
    def DELETE(cls, entity_type: Enum,
               target_value: Union[list, dict]) -> 'Operation':
        return Operation(Verbs.DELETE, entity_type, target_value)

    @classmethod
    def OVERWRITE(cls, entity_type: Enum,
                  target_value: Union[list, dict]) -> 'Operation':
        return Operation(Verbs.OVERWRITE, entity_type, target_value)


class Instruction(NamedTuple):
    operations: List[Operation]
    errors: Any = None
    redirect: str = ''

    def serialize(self) -> dict:
        ret = {}

        def dictify_value(value):
            if hasattr(value, "_asdict"):
                return dictify_value(value._asdict())
            elif isinstance(value, list):
                return [dictify_value(item) for item in value]
            elif isinstance(value, Enum):
                return value.name
            elif isinstance(value, dict):
                return {key: dictify_value(value[key]) for key in value}
            else:
                return value

        for field in self._fields:
            value = getattr(self, field)
            ret[field] = dictify_value(value)
        return ret


def config_instructor(routes: Dict[str, Type[RequestResolver]], entity_types):
    pass
