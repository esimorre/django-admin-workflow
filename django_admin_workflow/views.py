import os.path

from django.views.generic import TemplateView

from django_admin_workflow.utils import get_workflow_data


class WorkflowPageView(TemplateView):
    template_name = "django_admin_workflow/toml.html"

    def get_context_data(self, workflow, **kwargs):
        context = super().get_context_data(**kwargs)
        file = os.path.join(os.path.dirname(__file__), '..', workflow)
        with open(file, "r", encoding="utf-8") as f:
            context['body_toml'] = f.read()
        self.build_mermaid_diag(context, file)
        return context

    def build_mermaid_diag(self, context, file):
        dic_workflow = get_workflow_data(file_data=file)
        activity_by_status = {}
        links = []

        for role, dic_role in dic_workflow.items():
            for status, dic_status in dic_role.items():
                if status in ('filter', 'creation'): continue
                if status not in activity_by_status:
                    activity_by_status[status] = Activity(status=status, role=role)
                else:
                    activity_by_status[status].role = role
                if 'actions' not in dic_status: continue
                for action in dic_status['actions']:
                    if len(action) < 3: continue
                    action, label, status_dest = action
                    if status_dest not in activity_by_status:
                        activity_by_status[status_dest] = Activity(status=status_dest)

        for role, dic_role in dic_workflow.items():
            for status, dic_status in dic_role.items():
                if status in ('filter', 'creation'): continue
                activity = activity_by_status[status]
                if 'actions' not in dic_status: continue
                for action in dic_status['actions']:
                    if len(action) < 3: continue
                    action, label, status_dest = action
                    if action and label: activity_by_status[status].label.append(label)
                    if status_dest:
                        links.append(Link(start=status, end=status_dest, label=label))

        #context['merm_activities'] = ['DRAFT["DRAFT<hr/>fa:fa-user Vacation request<hr/>fa:fa-user-group employee "]',
        #                              'check("check<hr/>fa:fa-gear Check ")']
        context['merm_activities'] = activity_by_status.values()
        context['merm_actions'] = links
        #context['merm_actions'] = ['DRAFT -- "fa:fa-hand-pointer submit" --> check',
        #                           'check -- insufficient balance --> DRAFT']

# Mermaid graphics
class Activity:
    def __init__(self, status=None, role=None):
        self.label = []
        self.role = role
        self.status = status
    def __str__(self):
        symbol_role = "user-group"
        if self.status == "auto": symbol_role = "gear"
        tpl_user = "<hr/>fa:fa-user %s"
        if self.role == "auto": symbol_role = "gears"
        user = ""
        if self.label:
            if len(self.label) == 1: self.label = tpl_user % self.label[0]
            else:
                if self.status != "auto":
                    user = "<hr/>fa:fa-user-pen fa:fa-list"
        if not self.role:
            symbol_role = "trash-can"
            self.role = ""
        activity = '%s["fa:fa-tag %s%s<hr/>fa:fa-%s %s"]' %\
                    (self.status, self.status, user, symbol_role, self.role)
        return activity

class Link:
    def __init__(self, start, end, label=None):
        self.start = start
        self.end = end
        self.label = label
    def __str__(self):
        if self.label:
            link = '%s -- %s --> %s' % (self.start, self.label, self.end)
        else: link = '%s --> %s' % (self.start, self.end)
        return link
