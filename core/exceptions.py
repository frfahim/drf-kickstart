from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import (
    APIException,
    MethodNotAllowed,
    ValidationError,
)
from rest_framework.response import Response
from six import string_types
from rest_framework.serializers import as_serializer_error



class BaseException(Exception):
    """
    Internal exception base class that can be handled by the exception handler.
    """

    code = None
    error_code = None
    errors = None
    message = None
    identifier = None
    context = None
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(
        self,
        message="",
        context=None,
        errors=None,
        identifier=None,
        code=None,
        error_code=None,
        *args,
        **kwargs
    ):
        self.code = code or self.code
        self.error_code = error_code or self.error_code
        self.message = message or self.message or ""
        self.errors = errors or self.errors
        self.context = context or {}
        self.identifier = identifier

        if kwargs:
            self.context.update(kwargs)

        if self.context and self.message:
            self.message = self.message.format(**self.context)

    def __str__(self):
        return str(self.message)


class RequestTimeoutException(BaseException):
    errors = {
        "error_code": "REQUEST_TIMEOUT",
        "message": "Request timeout",
    }
    status_code = status.HTTP_408_REQUEST_TIMEOUT


class TimeOutExecption(BaseException):
    code = "REQUEST_TIMED_OUT"
    status_code = status.HTTP_408_REQUEST_TIMEOUT
    message = "Request Timed Out"


class BadRequestException(BaseException):
    code = "BAD_REQUEST"
    status_code = status.HTTP_400_BAD_REQUEST


class InvalidInputException(BadRequestException):
    code = "INVALID_INPUT"


class NotFoundException(BadRequestException):
    code = "NOT_FOUND"
    message = "Not found"
    status_code = status.HTTP_404_NOT_FOUND


class InvalidDateException(BadRequestException):
    code = "INVALID_DATE"
    message = "Invalid date"


class InvalidConfigurationException(BaseException):
    code = "INVALID_CONFIGURATION"
    message = "Invalid configuration of system. Please contact system administrator."


class ModuleNotSubscribedException(BaseException):
    code = "MODULE_NOT_SUBSCRIBED"
    message = "The requested feature is not subscribed by the tenant"


def exception_handler(exc, context=None):
    """
    Returns the response that should be used for any given exception.

    By default we handle the REST framework `APIException` and Django's builtin
    `Http404` exceptions.

    Any unhandled exceptions are catched and logged by this handler and
    an `OperationException` is raised accordingly the view or process behind
    that triggered the actual error.
    """

    if isinstance(exc, Http404):
        exc = NotFoundException()
    elif isinstance(exc, ValidationError):
        exc = InvalidInputException(errors=exc.detail)
    elif isinstance(exc, DjangoValidationError):
        exc = InvalidInputException(errors=exc.message_dict)

    # Make sure were always working with an APIException
    if not isinstance(exc, (APIException, BaseException)):
        raise exc

    identifier = getattr(exc, "identifier", None)
    code = getattr(exc, "code", "")
    message = getattr(exc, "message", "")
    error_code = getattr(exc, "error_code", "")
    errors = getattr(exc, "errors", [])

    if not code and isinstance(exc, APIException):
        if hasattr(exc, "get_codes"):
            codes = exc.get_codes()
            if isinstance(codes, string_types):
                code = codes
            else:
                code = next(iter(codes))

    if isinstance(exc, MethodNotAllowed):
        code = "NOT_ALLOWED"

    data = dict(
        message=message, errors=errors, key=identifier, code=code, error_code=error_code
    )

    return Response(data, status=exc.status_code)
