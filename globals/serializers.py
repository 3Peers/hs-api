from rest_framework import serializers
from .exceptions import HSBadArgumentException


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


def get_serializer_with_fields(model_serializer, fields):
    if not model_serializer.Meta:
        raise HSBadArgumentException('Serializer doesn\'t have Meta class.')

    if hasattr(model_serializer.Meta, 'exclude'):
        delattr(model_serializer.Meta, 'exclude')
    setattr(model_serializer.Meta, 'fields', fields)

    return model_serializer
