import json
from enum import auto, Enum
from typing import Type, Dict, Any, Union, NamedTuple, List, Callable, ClassVar

from django.db import transaction
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.http import JsonResponse as DjangoJsonResponse
from django.views import View

from marshmallow import class_registry
from slotomania.core import Sloto

from slotomania.exceptions import BadResolver
from slotomania.contrib.slots import AuthenticateUserRequest
from slotomania.contractor import Contract


class JsonResponse(DjangoJsonResponse):
    def __init__(self, data, *args, **kwargs) -> None:
        self.data = data
        super().__init__(data, *args, **kwargs)


class InstructorView(View):
    permission_classes: list = []
    routes: Dict[str, Type["RequestResolver"]]

    def get(self, request: Any, endpoint: str = None) -> JsonResponse:
        return JsonResponse({})

    @transaction.atomic
    def post(
        self, request: Any, endpoint: str, *args, **kwargs
    ) -> JsonResponse:
        """If mustate_state returns HttpResponse, return it."""
        request.data = json.loads(request.body)
        resolver = self.routes[endpoint](request=request, data=request.data)

        resolver.authenticate()
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
    target_value: Union[list, dict, str]

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
    def OVERWRITE(
        cls, entity_type: Enum, target_value: Union[list, dict, str]
    ) -> 'Operation':
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


class RequestResolver:
    # data: MyDataType
    resolve: Callable
    pre_action: ClassVar[str] = ""
    callback: ClassVar[str] = ""
    use_jwt_authentication: ClassVar[bool] = True

    def __init__(self, request, data: dict) -> None:
        self.request = request
        self._data = data
        self.clean_request_data()
        # Validate and create sloto data
        # self.validate()
        # self.data = sloto_klass.load_from_dict(self.validated_data)

    @classmethod
    def get_schema(cls):
        # TODO: deprecate schemas
        contract_class = cls.__annotations__["data"]
        return class_registry.get_class(contract_class.__name__)()

    def clean_request_data(self) -> None:
        contract_class = self.__class__.__annotations__["data"]
        if issubclass(contract_class, Sloto):
            schema = class_registry.get_class(contract_class.__name__)()
            self.validated_data = schema.load(self.request.data)
            self.data = contract_class.load_from_dict(self.validated_data)
        elif issubclass(contract_class, Contract):
            self.data = contract_class.load_from_dict(self.request.data)
        else:
            raise Exception(f"Unknown type for `data` f{contract_class}")

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if hasattr(cls, "resolve"):
            assert cls.__annotations__.get(
                "data"
            ), f"{cls} cannot define 'resovle' without annotating 'data'"
            if not cls.resolve.__annotations__:
                raise BadResolver(
                    f"{cls} must annotate resolve method if defined"
                )

    def authenticate(self) -> None:
        if not self.use_jwt_authentication:
            return

        from .contrib.jwt_auth import authenticate_request
        authenticate_request(self.request)


class EntityTypes(Enum):
    jwt_auth_token = auto()


class AuthenticateUser(RequestResolver):
    """Login and InitApp."""
    data: AuthenticateUserRequest
    use_jwt_authentication: ClassVar[bool] = False

    def resolve(self) -> Instruction:
        from .contrib.jwt_auth import jwt_encode_handler, jwt_payload_handler

        username = self.data.username
        password = self.data.password
        user = authenticate(username=username, password=password)

        if user:
            login(self.request, user)

            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)
            return Instruction(
                [Operation.OVERWRITE(EntityTypes.jwt_auth_token, token)]
            )

        return Instruction(operations=[], errors='bad credential')
