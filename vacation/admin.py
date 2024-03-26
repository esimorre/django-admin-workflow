from django.contrib import admin

from django_admin_workflow.admin import WorkflowModelAdmin
from django_admin_workflow.utils import get_workflow_data
from vacation.models import Vacation


@admin.register(Vacation)
class VacationAdmin(WorkflowModelAdmin):
    access_rules = get_workflow_data(__file__, file_data="workflow.toml")
    list_display = ('creator', 'begin', 'end', 'duration')
    list_filter = ('creator',)
