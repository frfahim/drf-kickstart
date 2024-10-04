class SerializerExcludeFieldsMixin:

    def __init__(self, *args, **kwargs):
        exclude = []
        fields = []
        if kwargs.get("exclude"):
            exclude = kwargs.pop("exclude")
        if kwargs.get("fields"):
            fields = kwargs.pop("fields")

        if fields and exclude:
            raise ValueError("exclude and fields cannot be used together")

        super().__init__(*args, **kwargs)

        if exclude:
            for field_name in exclude:
                self.fields.pop(field_name)

        """
        excludes fields which are not in fields list from serializer
        """

        temp_serializer_fields = self.fields.keys()
        excluded_fields = [field for field in temp_serializer_fields if field not in fields]
        if fields:
            for excluded_field in excluded_fields:
                self.fields.pop(excluded_field)
