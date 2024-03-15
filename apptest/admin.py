from django.contrib import admin

from apptest.models import MyTestModel
from django_admin_workflow.admin import WorkflowModelAdmin
from django_admin_workflow.utils import get_workflow_data


@admin.register(MyTestModel)
class MyTestModelAdmin(WorkflowModelAdmin):
    access_rules = get_workflow_data(__file__, file_data="workflow.toml")
    list_display = ('name', 'status_label', 'status', 'datetime', 'contact', 'duration', 'value', 'space', 'creator')
    list_filter = ('space', 'creator', 'status')
