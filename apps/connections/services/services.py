
from django.shortcuts import get_object_or_404
from ..models import Connection

def list_connections():
    return Connection.objects.filter(is_deleted=False).order_by('id')


def get_connection(pk, include_deleted=False):
    queryset = Connection.objects.all() if include_deleted else Connection.objects.filter(is_deleted=False)
    return get_object_or_404(queryset, pk=pk)


def delete_connection(instance):
    instance.is_deleted = True
    instance.save()


def update_connection(instance, validated_data):
    config_data = validated_data.pop('config', None)

    for attr, value in validated_data.items():
        setattr(instance, attr, value)

    if config_data is not None:
        instance.config = config_data

    instance.save()
    return instance

