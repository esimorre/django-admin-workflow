from django.contrib import admin

from .models import Analysis
from .workflow import StateModelAdmin


@admin.register(Analysis)
class AnalysisAdmin(StateModelAdmin):
    list_display = ('name', 'status', 'datetime', 'contact', 'duration', 'value', 'space', 'creator')
    list_filter = ('space', 'creator', 'status')
    save_as = True
