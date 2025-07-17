from django.contrib import admin, messages
from django.utils.html import format_html
from django.urls import path, reverse
from django.shortcuts import get_object_or_404, redirect
from django.db import models
from .models import WorkExecution

@admin.register(WorkExecution)
class WorkExecutionAdmin(admin.ModelAdmin):
    list_display = ("work", "status", "started_at", "short_message", "short_request", "short_response")
    search_fields = ("work__name", "status", "message", "request", "response")
    list_filter = ("status", "started_at")
    readonly_fields = ("started_at", "request", "response")

    def short_message(self, obj):
        if obj.message:
            return obj.message if len(obj.message) < 75 else obj.message[:72] + "..."
        return "-"
    short_message.short_description = "Message"

    def short_request(self, obj):
        if obj.request:
            return obj.request if len(obj.request) < 75 else obj.request[:72] + "..."
        return "-"
    short_request.short_description = "Request"

    def short_response(self, obj):
        if obj.response:
            return obj.response if len(obj.response) < 75 else obj.response[:72] + "..."
        return "-"
    short_response.short_description = "Response"

