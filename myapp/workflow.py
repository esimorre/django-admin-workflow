from django.db import models

from django_admin_workflow.admin import WorkflowModelAdmin
from django_admin_workflow.models import BaseStateModel

# Etats
class MyStatus(models.TextChoices):
    NEW      = "DRAFT", "Nouveau"
    SUBMIT   = "s", "Soumis"
    ACCEPTED = "a", "Accepté"
    VALID    = "v", "Validé"
    PUBLISH  = "p", "Publié"
    CANCELED = "c", "Annulé"


# classe de base pour le modèle et définition permission
class State(BaseStateModel):
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

        # partitionnement
        'filter': lambda q, user_space, user: q.filter(space=user_space),

        # accès des champs à la création
        'creation': {
            'fields': ['name', 'contact', 'status'],
            'readonly_fields': ['contact', 'status'],
        },

        MyStatus.NEW: {
            'perms': ['can_submit'],
            'fields': ['name', 'contact', 'status'],
            'readonly_fields': ['contact', 'status'],
            'actions': [('save', 'Enregistrer'),
                        ('submit', 'Soumettre', MyStatus.SUBMIT),
                        ('cancel', 'Annuler', MyStatus.CANCELED)],
        },
    }
}

# Gestionnaire des vues admin respectant les règles groupe/permissions/champs exposés
class StateModelAdmin(WorkflowModelAdmin):
    access_rules = _access_rules_analysis
