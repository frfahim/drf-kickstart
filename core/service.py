from django.core.exceptions import ObjectDoesNotExist
from django.db.models import QuerySet
from django.db.models.fields.related import ForeignKey



class BaseModelService:
    model = None

    def map_model_fields_and_data(self, defaults, model_class, *args, **kwargs):
        model_field_names_set = self.get_model_field_names(model_class)
        filtered_fields = {
            key: val for key, val in defaults.items() if key in model_field_names_set
        }
        return filtered_fields


    def get_model_field_names(self, model):
        model_field_names_set = set()

        if model:
            for field in model._meta.get_fields():
                if isinstance(field, ForeignKey):
                    db_field_name = field.name + "_id"
                    keys = [field.name, db_field_name]
                else:
                    keys = [field.name]
                model_field_names_set.update(keys)

        return model_field_names_set

    def create_model_instance(self, model_class, **field_values):
        filtered_fields = self.map_model_fields_and_data(field_values, model_class())
        if hasattr(model_class, "created_by"):
            if filtered_fields.get("created_by") or filtered_fields.get(
                "created_by_id"
            ):
                pass
            else:
                user = self.user if hasattr(self, "user") else self.kwargs.get("user")
                if user:
                    filtered_fields.update({"created_by_id": user.id})
        instance = model_class(**filtered_fields)
        instance.save()
        return instance

    def create(self, *args, **kwargs):
        return self.create_model_instance(self.model, **kwargs)

    def bulk_create(self, model_object_list: list) -> QuerySet:
        obj_list = []
        for model_obj in model_object_list:
            filtered_fields = self.map_model_fields_and_data(model_obj, self.model())
            obj_list.append(self.model(**filtered_fields))
        bulk_instance = self.model.objects.none()
        if obj_list:
            bulk_instance = self.model.objects.bulk_create(obj_list)
        return bulk_instance

    def update_model_instance(self, instance, **field_values):
        model_class = instance.__class__
        filtered_fields = self.map_model_fields_and_data(field_values, model_class())
        for key, val in filtered_fields.items():
            setattr(instance, key, val)
        # set updated_by from request user
        if hasattr(model_class, "updated_by"):
            # if any of this two field exist then updated_by already assigned
            if filtered_fields.get("updated_by") or filtered_fields.get(
                "updated_by_id"
            ):
                pass
            else:
                user = self.user if hasattr(self, "user") else self.kwargs.get("user")
                if user:
                    instance.updated_by_id = user.id
        instance.save()
        return instance

    def _get_queryset(self, **query_params):
        queryset = self.model.objects.all()
        if query_params:
            queryset = queryset.filter(**query_params)
        return queryset

    def read_by_pk(self, pk_value, **kwargs):
        try:
            return self._get_queryset(**kwargs).get(pk=pk_value)
        except self.model.DoesNotExist:
            raise ObjectDoesNotExist

    def read_by_uuid(self, uuid_value, **kwargs):
        try:
            return self._get_queryset(**kwargs).get(uuid=uuid_value)
        except self.model.DoesNotExist:
            raise ObjectDoesNotExist

    def read_by_code(self, code_value, **kwargs):
        try:
            return self._get_queryset(**kwargs).get(code=code_value)
        except self.model.DoesNotExist:
            raise ObjectDoesNotExist

    def _sort_queryset(self, queryset, query_params):
        if query_params:
            queryset = queryset.order_by(*query_params)
        return queryset

    def list(self, **query_params):
        queryset = self._get_queryset()
        if query_params:
            queryset = queryset.filter(**query_params)
        queryset = self._sort_queryset(queryset=queryset, query_params=query_params)
        if hasattr(self.model, "sort_order"):
            queryset = queryset.order_by("sort_order")
        return queryset

    def create_or_update(self, read_by="code", **field_values):
        read_by_value = field_values.get(read_by, None)
        if read_by_value and hasattr(self, "read_by_" + read_by):
            try:
                model_instance = getattr(self, "read_by_" + read_by)(read_by_value)
            except ObjectDoesNotExist:
                model_instance = self.create_model_instance(self.model, **field_values)
            else:
                model_instance = self.update_model_instance(
                    model_instance, **field_values
                )
            return model_instance
