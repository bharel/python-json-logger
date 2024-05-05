"""JSON formatter using the standard library's `json` for encoding.

Module contains the `JsonFormatter` and a custom `JsonEncoder` which supports a greater
variety of types.
"""

### IMPORTS
### ============================================================================
## Future
from __future__ import annotations

## Standard Library
from datetime import date, datetime, time
from inspect import istraceback
import json
import traceback
from typing import Any, Callable, Optional, Union
import warnings

## Application
from . import core


### CLASSES
### ============================================================================
class JsonEncoder(json.JSONEncoder):
    """A custom encoder extending the default JSONEncoder

    Refs:
    - https://docs.python.org/3/library/json.html
    """

    def default(self, o: Any) -> Any:
        if isinstance(o, (date, datetime, time)):
            return self.format_datetime_obj(o)

        if istraceback(o):
            return "".join(traceback.format_tb(o)).strip()

        # pylint: disable=unidiomatic-typecheck
        if type(o) == Exception or isinstance(o, Exception) or type(o) == type:
            return str(o)

        try:
            return super().default(o)

        except TypeError:
            try:
                return str(o)

            except Exception:  # pylint: disable=broad-exception-caught
                return None

    def format_datetime_obj(self, o):
        """Format datetime objects found in self.default

        This allows subclasses to change the datetime format without understanding the
        internals of the default method.
        """
        return o.isoformat()


class JsonFormatter(core.BaseJsonFormatter):
    """JSON formatter using the standard library's `json` for encoding"""

    def __init__(
        self,
        *args,
        json_default: core.OptionalCallableOrStr = None,
        json_encoder: core.OptionalCallableOrStr = None,
        json_serializer: Union[Callable, str] = json.dumps,
        json_indent: Optional[Union[int, str]] = None,
        json_ensure_ascii: bool = True,
        **kwargs,
    ) -> None:
        """
        Args:
            json_default: a function for encoding non-standard objects
                as outlined in https://docs.python.org/3/library/json.html
            json_encoder: optional custom encoder
            json_serializer: a :meth:`json.dumps`-compatible callable
                that will be used to serialize the log record.
            json_indent: indent parameter for json.dumps
            json_ensure_ascii: ensure_ascii parameter for json.dumps
        """
        super().__init__(*args, **kwargs)

        self.json_default = core.str_to_object(json_default)
        self.json_encoder = core.str_to_object(json_encoder)
        self.json_serializer = core.str_to_object(json_serializer)
        self.json_indent = json_indent
        self.json_ensure_ascii = json_ensure_ascii
        if not self.json_encoder and not self.json_default:
            self.json_encoder = JsonEncoder
        return

    def jsonify_log_record(self, log_record: core.LogRecord) -> str:
        return self.json_serializer(
            log_record,
            default=self.json_default,
            cls=self.json_encoder,
            indent=self.json_indent,
            ensure_ascii=self.json_ensure_ascii,
        )


### DEPRECATED COMPATIBILITY
### ============================================================================
def __getattr__(name: str):
    if name == "RESERVED_ATTRS":
        warnings.warn(
            "RESERVED_ATTRS has been moved to pythonjsonlogger.core",
            DeprecationWarning,
        )
        return core.RESERVED_ATTRS
    raise AttributeError(f"module {__name__} has no attribute {name}")