from django.contrib import admin, messages
from django.urls import path, reverse
from django.shortcuts import get_object_or_404, redirect
from django.utils.html import format_html

from .models import Connection
from apps.connections.api_connections_views import test_connection_logic 


@admin.register(Connection)
class ConnectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'owner', 'is_active', 'updated_at', 'test_button')
    list_filter = ('type', 'is_active')
    search_fields = ('name', 'owner__email')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ("General Information", {
            "fields": ("name", "type", "owner", "is_active")
        }),
        ('Configuration', {
            'fields': ('config',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
        }),
    )

    def get_urls(self):
        custom_urls = [
            path(
                '<int:connection_id>/test/',
                self.admin_site.admin_view(self.test_connection_view),
                name='connections_connection_test',  # ← nombre correcto para reverse()
            ),
        ]
        return custom_urls + super().get_urls()

    def test_button(self, obj):
        url = reverse('admin:connections_connection_test', args=[obj.pk])  # ← uso correcto con namespace "admin:"
        return format_html('<a class="button" href="{}">Test Connection</a>', url)

    test_button.short_description = 'Test'
    test_button.allow_tags = True

    def test_connection_view(self, request, connection_id):
        connection = Connection.objects.get(pk=connection_id)

        try:
            payload = {
                "type": connection.type,
                "config": connection.config
            }

            factory = RequestFactory()
            fake_request = factory.post(
                "/admin/test/",
                data=json.dumps(payload),
                content_type="application/json"
            )
            fake_request.user = request.user  # Required for DRF APIView
            response = TestConnectionAPIView.as_view()(fake_request)
            data = response.data if hasattr(response, "data") else response.json()

            if data.get("ok") or data.get("status") == 200:
                self.message_user(request, "✅ Connection successful.", messages.SUCCESS)
            else:
                self.message_user(request, f"❌ Connection failed: {data}", messages.ERROR)

        except Exception as e:
            self.message_user(request, f"❌ Error testing connection: {str(e)}", messages.ERROR)

        return redirect(reverse('admin:connections_connection_change', args=[connection.pk]))  # Ajusta según tu app name


    class Media:
        js = ('admin/js/connection_config_generator.js',)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:connection_id>/test/',
                self.admin_site.admin_view(self.test_connection_logic_view),
                name='connection_test',
            ),
        ]
        return custom_urls + urls

    def test_button(self, obj):
        url = reverse('admin:connection_test', args=[obj.pk])
        return format_html(
            '<a class="button" href="{}" style="padding:4px 8px; background:#17a2b8; color:#fff; border-radius:4px;">Test</a>',
            url
        )
    test_button.short_description = "Test Connection"

    def test_connection_logic_view(self, request, connection_id):
        connection = get_object_or_404(Connection, pk=connection_id)
        try:
            result = test_connection_logic(connection)  # ✅ Correct call
            messages.success(request, f"✅ Connection successful: {result.get('message', result)}")
        except Exception as e:
            messages.error(request, f"❌ Connection failed: {str(e)}")
        return redirect(request.META.get('HTTP_REFERER', '/admin/'))
