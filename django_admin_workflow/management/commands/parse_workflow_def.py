from django.core.management import BaseCommand


class Command(BaseCommand):
    help = """Parse a workflow definition file (see gen_workflow_template) then generate objects in db.
    
    The command generates:
    GROUP_NAME -> group ;
    OTHER_STATUS, STATUS_TARGET -> Status ;
    fields, readonly_fields -> workflow model template (on stdout) ;
    PERM_CODE_NAME -> Permission (only if the workflow model is defined in models.py)
    """

    def add_arguments(self, parser):
        parser.add_argument("workflow_file",
                            help="file typically [myapp]/workflow.py")
        parser.add_argument("-d", "--doc", action='store_true',
                            required=False, help="generate a markdown workflow documentation.")

    def handle(self, *args, **options):
        print("TODO")
