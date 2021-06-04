from django.contrib import admin
from .models import User
# Register your models here


@admin.register(User)
class UserAdminSite(admin.ModelAdmin):
    list_display = ("username", "email")
    search_fields = ("username__startswith",)
    list_filter = ("is_staff",)
