from django.contrib import admin
from django import forms
from .models import User, Role

# Custom form for the User model to include 'name' and 'role'
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = '__all__'

class UserAdmin(admin.ModelAdmin):
    # Use the custom form
    form = UserForm

    # Display the desired fields in the list view
    list_display = ('username', 'email', 'name', 'is_active', 'role')

    # Add search functionality for 'username', 'email', 'first_name', 'last_name', 'name'
    search_fields = ('username', 'email', 'first_name', 'last_name', 'name')

    # Exclude fields from the admin form
    exclude = ('first_name', 'last_name', 'groups', 'user_permissions', 'password')

# Register the User model with the custom UserAdmin
admin.site.register(User, UserAdmin)
admin.site.register(Role)