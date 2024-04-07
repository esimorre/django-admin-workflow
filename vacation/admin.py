from django.contrib import admin
from django.contrib.admin import ModelAdmin

from django_admin_workflow.admin import WorkflowModelAdmin, ExecutorAdmin
from django_admin_workflow.utils import get_workflow_data
from .models import Vacation, UserAccount, VacationExecutor


@admin.register(Vacation)
class VacationAdmin(WorkflowModelAdmin):
    access_rules = get_workflow_data(__file__, file_data="workflow.toml")
    list_display = ('creator', 'status', 'space', 'begin', 'end', 'duration')
    list_filter = ('creator',)

@admin.register(UserAccount)
class UserAccountAdmin(ModelAdmin):
    list_display = ('user', 'provision')

@admin.register(VacationExecutor)
class VacationExecutorAdmin(ExecutorAdmin):
    pass