import typing

from .exceptions import NotAuthenticated

FuncType = typing.TypeVar('FuncType', bound=typing.Callable[..., typing.Any])


class Command:
    resolve: typing.Callable
    require_authentication: bool = True
    ContextValidator: typing.ClassVar = None
    Presenter: typing.ClassVar = None

    def validate_context(self) -> None:
        validator = self.ContextValidator()
        validator.load(self.context)

    def present(self, data, many=False, validate=True) -> dict:
        presenter = self.Presenter(many=many)
        presenter.context['request'] = self.request
        ret = presenter.dump(data)
        if validate:
            presenter.load(ret)

        return ret

    def __init__(self, context: dict, request=None) -> None:
        self.context = context
        self.request = request

    @classmethod
    def validate_class(cls) -> None:
        if hasattr(cls, 'resolve') and not getattr(cls, 'ContextValidator'):
            raise AssertionError(f'You forgot to define ContextValidator for {cls}')

    def __init_subclass__(cls, *args, **kwargs):
        cls.validate_class()

        # Auto register command and its ContextValidator
        if hasattr(cls, 'resolve'):
            register_command(cls.__name__)(cls)
            if getattr(cls, 'ContextValidator'):
                register_function(cls.__name__)(cls.ContextValidator)

    def authenticate(self) -> None:
        if self.require_authentication and not self.request.user.is_authenticated:
            raise NotAuthenticated()

    def dispatch(self, state):
        self.authenticate()
        self.validate_context()
        return self.resolve(state)


class Registry:
    interfaces: typing.ClassVar[typing.Dict] = {}
    functions: typing.ClassVar[typing.Dict] = {}
    commands: typing.ClassVar[typing.Dict[str, typing.Type[Command]]] = {}


def register_command(name: str) -> FuncType:
    def wrapper(cls: typing.Type[Command]):
        assert name not in Registry.commands
        Registry.commands[name] = cls
        return cls

    return typing.cast(FuncType, wrapper)


def register_function(name: str):
    def wrapper(cls):
        assert name not in Registry.functions
        Registry.functions[name] = cls
        return cls

    return wrapper


def register_interface(cls):
    """Use as a class decorator to register a schema as a
    typescript interface
    """
    assert cls.__name__ not in Registry.interfaces
    Registry.interfaces[cls.__name__] = cls
    return cls
