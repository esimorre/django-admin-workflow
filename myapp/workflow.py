from django.db import models

from django_admin_workflow.admin import WorkflowModelAdmin
from django_admin_workflow.models import BaseStateModel

# Etats
class Status(models.TextChoices):
    NEW      = "n", "Nouveau"
    ACCEPTED = "a", "Accepté"
    VALID    = "v", "Validé"
    PUBLISH  = "p", "Publié"


# classe de base pour le modèle et définition permission
class State(BaseStateModel):
    status = models.CharField(max_length=1, choices=Status, default=Status.NEW)

    class Meta:
        abstract = True
        permissions = [("can_submit", "Rôle demandeur"),
                       ("can_accept", "Rôle accepteur"),
                       ("can_valid", "Rôle valideur"),
                       ("can_publish", "Rôle publieur"),]

# règles d'accès admin
_access_rules_analysis = {
    # Groupe "clients"
    'clients': {

        'creation': {
            'fields': ['name', 'contact', 'status'],
            'readonly_fields': ['contact', 'status'],
        },

        'filter': lambda q, user_space, user: q.filter(space=user_space.group.name),

        Status.NEW: {
            'perms': ['can_submit'],
            'fields': ['name', 'contact', 'status'],
            'readonly_fields': ['contact', 'status'],
            'actions': [('submit', 'Modifier'), ('cancel', 'Annuler')],
        },
    }
}

# Gestionnaire des vues admin respectant les règles groupe/permissions/champs exposés
class StateModelAdmin(WorkflowModelAdmin):
    access_rules = _access_rules_analysis
