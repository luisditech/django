
from django.contrib import admin
from .models import HomologationRule
from django.utils.html import format_html

@admin.register(HomologationRule)
class HomologationRuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'download_csv_link')
    readonly_fields = ('created_at',)

    def download_csv_link(self, obj):
        if obj.csv_file:
            return format_html('<a href="{}" download>Descargar CSV</a>', obj.csv_file.url)
        return "Sin archivo"
    download_csv_link.short_description = "Archivo CSV"

