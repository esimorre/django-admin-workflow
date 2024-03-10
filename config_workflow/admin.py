from django.contrib import admin

from .models import *

@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ('slug', 'verbose_name', 'ctype')


class FieldsInline(admin.TabularInline):
    def get_formset(self, request, obj=None, **kwargs):
        self._list_wfields = self._list_fields_workflow_model(obj)
        formset = super().get_formset(request, obj, **kwargs)
        return formset

    def list_wfields(self):
        return " , ".join(self._list_wfields)

    def _list_fields_workflow_model(self, config_role_ob):
        cls = config_role_ob.config.ctype.model_class()
        fields = [f.attname for f in cls._meta.fields]
        return fields

class ConfigRoleAddInline(FieldsInline):
    template = "config_workflow/edit_inline/tabular.html"
    model = ConfigRoleAdd
    extra = 1

class RoleStatusActionInline(admin.TabularInline):
    model = RoleStatusAction
    extra = 1

class ConfigRoleStatusInline(FieldsInline):
    template = "config_workflow/edit_inline/tabular.html"
    model = ConfigRoleStatus
    show_change_link = True
    extra = 1


class ConfigRoleInline(admin.StackedInline):
    template = "config_workflow/edit_inline/tabular.html"
    model = ConfigRole
    show_change_link = True
    extra = 1


@admin.register(ConfigWorkflow)
class ConfigWorkflowAdmin(admin.ModelAdmin):
    inlines = [ConfigRoleInline]
    list_display = ('label', 'ctype')

    def get_queryset(self, request):
        return super().get_queryset(request)


@admin.register(ConfigRole)
class ConfigRoleAdmin(admin.ModelAdmin):
    inlines = [ConfigRoleAddInline, ConfigRoleStatusInline]
    list_display = ('role', 'config')
    fields = (('role', 'config'), ('filter_space', 'filter_user'))
    readonly_fields = ('role', 'config')

    def has_add_permission(self, request):
        return False


@admin.register(ConfigRoleStatus)
class ConfigRoleStatusAdmin(admin.ModelAdmin):
    inlines = [RoleStatusActionInline]
    list_display = ('status', 'config_role', 'workflow_name')
    fields = (('config_role', 'status', 'permission'), 'edit_fields', 'readonly_fields')
    readonly_fields = ('config_role', 'status', 'permission')

    def has_add_permission(self, request):
        return False
