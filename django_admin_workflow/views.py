import os.path

from django.shortcuts import render
from django.views.generic import TemplateView


class WorkflowPageView(TemplateView):
    template_name = "django_admin_workflow/toml.html"

    def get_context_data(self, workflow='apptest/workflow.toml', **kwargs):
        context = super().get_context_data(**kwargs)
        file = os.path.join(os.path.dirname(__file__), '..', workflow)
        with open(file, "r", encoding="utf-8") as f:
            context['body_toml'] = f.read()
        return context