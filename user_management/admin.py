from django.contrib import admin
from .models import Page, UserPageAssignment


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('name', 'url_path', 'is_active', 'created_at')
    search_fields = ('name', 'url_path')
    list_filter = ('is_active',)
    list_editable = ('is_active',)


@admin.register(UserPageAssignment)
class UserPageAssignmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'page', 'assigned_by', 'assigned_on')
    search_fields = ('user__username', 'page__name')
    list_filter = ('page',)
    readonly_fields = ('assigned_by', 'assigned_on')

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.assigned_by = request.user
        super().save_model(request, obj, form, change)
