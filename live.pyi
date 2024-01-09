import typing

T = typing.TypeVar("T")

class lazy_attribute(typing.Generic[T]):
    def __init__(self, func: typing.Callable[[typing.Any], T], name=...) -> None: ...
    def __get__(self, obj, cls=...) -> T: ...
