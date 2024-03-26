import os.path

from django.views.generic import TemplateView


class WorkflowPageView(TemplateView):
    template_name = "django_admin_workflow/toml.html"

    def get_context_data(self, workflow, **kwargs):
        context = super().get_context_data(**kwargs)
        file = os.path.join(os.path.dirname(__file__), '..', workflow)
        with open(file, "r", encoding="utf-8") as f:
            context['body_toml'] = f.read()
        self.build_mermaid_diag(context)
        return context

    def build_mermaid_diag(self, context):
        context['merm_activities'] = ['DRAFT["DRAFT<hr/>fa:fa-user Vacation request<hr/>fa:fa-user-group employee "]',
                                      'check("check<hr/>fa:fa-gear Check ")']
        context['merm_actions'] = ['DRAFT -- "fa:fa-hand-pointer submit" --> check',
                                   'check -- insufficient balance --> DRAFT']