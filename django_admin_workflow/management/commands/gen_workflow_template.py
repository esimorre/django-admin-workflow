from django.core.management import BaseCommand


_template = """
{
    'GROUP_NAME': {
        # filter on space
        'filter': lambda q, user_space, user: q.filter(space=user_space),
        # field access on creation
        'creation': {
            'fields': ['name', 'contact', 'status'],
            'readonly_fields': ['contact', 'status'],
        },
        # The 'DRAFT' status is the default for all workflow models
        'DRAFT': {
            'perms': [PERM_CODE_NAME,],
            'fields': ['name', 'contact', 'status'],
            'readonly_fields': ['contact', 'status'],
            'actions': [('save', 'Save'),
                        ('submit', 'Submit', "accepted"),
                        # (ROLE_PERM, ROLE_PERM_VERBOSE [, STATUS_TARGET])
                        ('cancel', 'Cancel', "canceled")],
        },
        OTHER_STATUS: {
            # see 'DRAFT' status above
        },
    }
}

"""

class Command(BaseCommand):
    help = "Generate a workflow template file"

    def add_arguments(self, parser):
        pass
    def handle(self, *args, **options):
        print(_template)
        print("### Put this in a file named 'workflow.py' in your app directory ###")
