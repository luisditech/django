from rest_framework import serializers
from .models import Connection

class ConnectionSerializer(serializers.ModelSerializer):
    config = serializers.DictField(write_only=True, required=False)
    data = serializers.SerializerMethodField()

    class Meta:
        model = Connection
        fields = ['id', 'name', 'type', 'owner', 'created_at', 'updated_at', 'config', 'data', 'is_active']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data):
        connection_type = data.get("type") or self.instance.type
        config = data.get("config", self.instance.config if self.instance else {})

        required_fields = {
            "sftp": ['host', 'port', 'username', 'password'],
            "shopify": ['shop_url', 'api_key', 'password'],
            "restlet": [
                'base_url', 'consumer_key', 'consumer_secret',
                'token_key', 'token_secret', 'realm', 'script_id', 'deploy_id'
            ]
        }

        expected = required_fields.get(connection_type, [])
        missing = [field for field in expected if field not in config]

        if missing:
            raise serializers.ValidationError({
                'config': f"Missing fields for {connection_type}: {', '.join(missing)}"
            })

        return data

    def create(self, validated_data):
        config_data = validated_data.pop('config', {})
        connection = Connection.objects.create(**validated_data, config=config_data)
        return connection

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.type = validated_data.get('type', instance.type)
        instance.owner = validated_data.get('owner', instance.owner)
        config_data = validated_data.get('config', None)

        if config_data is not None:
            instance.config = config_data

        instance.save()
        return instance

    def get_data(self, obj):
        return obj.config or {}
