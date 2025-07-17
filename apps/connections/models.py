from django.db import models
from django.core.exceptions import ValidationError
from apps.core.models import User

CONNECTION_TYPES = (
    ("shopify", "Shopify"),
    ("sftp", "SFTP"),
    ("ftp", "FTP"),
    ("rest", "REST API"),
    ("graphql", "GraphQL API"),
    ("netsuite", "NetSuite"),
    ("restlet", "RESTlet"),
    ("postgresql", "PostgreSQL"),  # ✅ Added PostgreSQL
)

class Connection(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=CONNECTION_TYPES)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='connections')
    config = models.JSONField(default=dict, blank=True, help_text="Dynamically generated configuration")
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.type})"

    def clean(self):
        required_fields = {
            "shopify": ["shop_url", "api_key", "password"],
            "sftp": ["host", "port", "username", "password"],
            "ftp": ["host", "port", "username", "password"],
            "rest": ["base_url"],
            "graphql": ["base_url"],
            "netsuite": [
                "account", "consumer_key", "consumer_secret",
                "token_key", "token_secret", "realm",
                "script_id", "deploy_id"
            ],
            "postgresql": ["host", "port", "dbname", "user", "password"], 
        }

        required = required_fields.get(self.type, [])
        missing = [field for field in required if field not in self.config or not self.config[field]]

        if missing:
            raise ValidationError(f"Missing config keys for {self.type}: {', '.join(missing)}")
