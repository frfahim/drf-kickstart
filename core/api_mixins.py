import re

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.response import Response


class CreateAPIMixin:
    def prepare_raw_data(self, request, *args, **kwargs):
        request_data = request.data
        return request_data

    def create(self, request, *args, **kwargs):
        raw_data = self.prepare_raw_data(request, *args, **kwargs)
        serializer = self.get_serializer(data=raw_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        if (
            serializer.instance
            and hasattr(self, "output_serializer_class")
            and self.output_serializer_class
        ):
            output_serializer = self.output_serializer_class(
                serializer.instance, context=self.get_serializer_context()
            )
            output_serializer_data = output_serializer.data
        else:
            output_serializer_data = serializer.data
        headers = self.get_success_headers(output_serializer_data)
        return Response(
            output_serializer_data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer):
        service = self.service_class()
        try:
            create_data = serializer.validated_data
            create_data["created_by_id"] = self.request.user.id
            serializer.instance = service.create(**create_data)
        except ValidationError as ex:
            if hasattr(ex, "message_dict"):
                raise DRFValidationError(ex.message_dict)
            else:
                raise DRFValidationError(ex)
        except ObjectDoesNotExist as ex:
            raise NotFound(detail=ex.message)


class RetrieveAPIMixin:
    def get_queryset(self):
        query_params = self.request.query_params.dict()
        return self.service_class().list(**query_params)

    def get_object(self):
        query_params = self.request.query_params.dict()
        service = self.service_class()

        if self.read_by == "code":
            code = self.kwargs.get("code")
            return service.read_by_code(code, **query_params)
        uuid = self.kwargs.get("uuid")
        return service.read_by_uuid(uuid, **query_params)


class ListAPIMixin:
    def get_queryset(self):
        return self.service_class().list()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if hasattr(self, "sort_order"):
            queryset = queryset.order_by(self.sort_order)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(
                page, many=True, context={"request": request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(
            queryset, many=True, context={"request": request}
        )
        return Response(serializer.data)
