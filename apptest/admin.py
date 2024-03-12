from django.contrib import admin

from apptest.models import MyTestModel
from django_admin_workflow.admin import WorkflowModelAdmin


@admin.register(MyTestModel)
class MyTestModelAdmin(WorkflowModelAdmin):
    list_display = ('name', 'status', 'datetime', 'contact', 'duration', 'value', 'space', 'creator')
    list_filter = ('space', 'creator', 'status')
    # clients -> submiter
    #create_states(("accepted", "valid", "published",))
    #create_roles(("submiter", "validator", "publisher"))
    access_rules = {
        'clients': {
            'filter': lambda q, user_space, user: q.filter(space=user_space),
            'creation': {
                'fields': ['name', 'contact', 'status'],
                'readonly_fields': ['contact', 'status'],
            },
            'DRAFT': {
                'perms': ['can_submit'],
                'fields': ['name', 'contact', 'status'],
                'readonly_fields': ['contact', 'status'],
                'actions': [('save', 'Enregistrer'),
                            ('submit', 'Soumettre', "accepted"),
                            ('cancel', 'Annuler', "canceled")],
            },
        }
    }
