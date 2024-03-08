from django.db import models


class BaseState(models.Model):
    class Status(models.TextChoices):
        DRAFT = "d", "Draft"
        PUBLISH = "p", "Published"

    status = models.CharField(max_length=1, choices=Status, default=Status.DRAFT)
    space = models.CharField(max_length=40, default='default', editable=False)
    creator = models.CharField(max_length=40, default='admin', editable=False)

    class Meta:
        abstract = True
        permissions = [("can_edit", "Editor role"),
                       ("can_publish", "Publisher role"),]

# règles d'accès admin
_access_rules_analysis = {
    # Groupe "clients"
    'editors': {

        'creation': {
            'fields': ['name', 'contact', 'status'],
            'readonly_fields': ['contact', 'status'],
        },

        #'filter': lambda q, space, user: q.filter(contact__user=user),

        BaseState.Status.DRAFT: {
            'perms': ['can_edit'],
            'fields': ['name', 'contact', 'status'],
            'readonly_fields': ['contact', 'status'],
            'actions': [('can_edit', 'Modifier'), ('cancel', 'Annuler')],
        },
    }
}
