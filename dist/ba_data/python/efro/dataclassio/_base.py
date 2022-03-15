# Released under the MIT License. See LICENSE for details.
#
"""Core components of dataclassio."""

from __future__ import annotations

import dataclasses
import typing
import datetime
from enum import Enum
from typing import TYPE_CHECKING, get_args
# noinspection PyProtectedMember
from typing import _AnnotatedAlias  # type: ignore

if TYPE_CHECKING:
    from typing import Any, Optional

# Types which we can pass through as-is.
SIMPLE_TYPES = {int, bool, str, float, type(None)}

# Attr name for dict of extra attributes included on dataclass instances.
# Note that this is only added if extra attributes are present.
EXTRA_ATTRS_ATTR = '_DCIOEXATTRS'


def _raise_type_error(fieldpath: str, valuetype: type,
                      expected: tuple[type, ...]) -> None:
    """Raise an error when a field value's type does not match expected."""
    assert isinstance(expected, tuple)
    assert all(isinstance(e, type) for e in expected)
    if len(expected) == 1:
        expected_str = expected[0].__name__
    else:
        names = ', '.join(t.__name__ for t in expected)
        expected_str = f'Union[{names}]'
    raise TypeError(f'Invalid value type for "{fieldpath}";'
                    f' expected "{expected_str}", got'
                    f' "{valuetype.__name__}".')


class Codec(Enum):
    """Specifies expected data format exported to or imported from."""

    # Use only types that will translate cleanly to/from json: lists,
    # dicts with str keys, bools, ints, floats, and None.
    JSON = 'json'

    # Mostly like JSON but passes bytes and datetime objects through
    # as-is instead of converting them to json-friendly types.
    FIRESTORE = 'firestore'


class IOExtendedData:
    """A class that data types can inherit from for extra functionality."""

    def will_output(self) -> None:
        """Called before data is sent to an outputter.

        Can be overridden to validate or filter data before
        sending it on its way.
        """

    @classmethod
    def will_input(cls, data: dict) -> None:
        """Called on raw data before a class instance is created from it.

        Can be overridden to migrate old data formats to new, etc.
        """


def _is_valid_for_codec(obj: Any, codec: Codec) -> bool:
    """Return whether a value consists solely of json-supported types.

    Note that this does not include things like tuples which are
    implicitly translated to lists by python's json module.
    """
    if obj is None:
        return True

    objtype = type(obj)
    if objtype in (int, float, str, bool):
        return True
    if objtype is dict:
        # JSON 'objects' supports only string dict keys, but all value types.
        return all(
            isinstance(k, str) and _is_valid_for_codec(v, codec)
            for k, v in obj.items())
    if objtype is list:
        return all(_is_valid_for_codec(elem, codec) for elem in obj)

    # A few things are valid in firestore but not json.
    if issubclass(objtype, datetime.datetime) or objtype is bytes:
        return codec is Codec.FIRESTORE

    return False


class IOAttrs:
    """For specifying io behavior in annotations."""

    storagename: Optional[str] = None
    store_default: bool = True
    whole_days: bool = False
    whole_hours: bool = False

    def __init__(self,
                 storagename: Optional[str] = storagename,
                 store_default: bool = store_default,
                 whole_days: bool = whole_days,
                 whole_hours: bool = whole_hours):

        # Only store values that differ from class defaults to keep
        # our instances nice and lean.
        cls = type(self)
        if storagename != cls.storagename:
            self.storagename = storagename
        if store_default != cls.store_default:
            self.store_default = store_default
        if whole_days != cls.whole_days:
            self.whole_days = whole_days
        if whole_hours != cls.whole_hours:
            self.whole_hours = whole_hours

    def validate_for_field(self, cls: type, field: dataclasses.Field) -> None:
        """Ensure the IOAttrs instance is ok to use with the provided field."""

        # Turning off store_default requires the field to have either
        # a default_factory or a default
        if not self.store_default:
            default_factory: Any = field.default_factory
            if (default_factory is dataclasses.MISSING
                    and field.default is dataclasses.MISSING):
                raise TypeError(f'Field {field.name} of {cls} has'
                                f' neither a default nor a default_factory;'
                                f' store_default=False cannot be set for it.')

    def validate_datetime(self, value: datetime.datetime,
                          fieldpath: str) -> None:
        """Ensure a datetime value meets our value requirements."""
        if self.whole_days:
            if any(x != 0 for x in (value.hour, value.minute, value.second,
                                    value.microsecond)):
                raise ValueError(
                    f'Value {value} at {fieldpath} is not a whole day.')
        if self.whole_hours:
            if any(x != 0
                   for x in (value.minute, value.second, value.microsecond)):
                raise ValueError(f'Value {value} at {fieldpath}'
                                 f' is not a whole hour.')


def _get_origin(anntype: Any) -> Any:
    """Given a type annotation, return its origin or itself if there is none.

    This differs from typing.get_origin in that it will never return None.
    This lets us use the same code path for handling typing.List
    that we do for handling list, which is good since they can be used
    interchangeably in annotations.
    """
    origin = typing.get_origin(anntype)
    return anntype if origin is None else origin


def _parse_annotated(anntype: Any) -> tuple[Any, Optional[IOAttrs]]:
    """Parse Annotated() constructs, returning annotated type & IOAttrs."""
    # If we get an Annotated[foo, bar, eep] we take
    # foo as the actual type, and we look for IOAttrs instances in
    # bar/eep to affect our behavior.
    ioattrs: Optional[IOAttrs] = None
    if isinstance(anntype, _AnnotatedAlias):
        annargs = get_args(anntype)
        for annarg in annargs[1:]:
            if isinstance(annarg, IOAttrs):
                if ioattrs is not None:
                    raise RuntimeError(
                        'Multiple IOAttrs instances found for a'
                        ' single annotation; this is not supported.')
                ioattrs = annarg

            # I occasionally just throw a 'x' down when I mean IOAttrs('x');
            # catch these mistakes.
            elif isinstance(annarg, (str, int, float, bool)):
                raise RuntimeError(
                    f'Raw {type(annarg)} found in Annotated[] entry:'
                    f' {anntype}; this is probably not what you intended.')
        anntype = annargs[0]
    return anntype, ioattrs
