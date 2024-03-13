from django.core.management import BaseCommand


class Command(BaseCommand):

    help = """import a workflow definition file (see gen_workflow_template) to generate objects in db.
    This command generates groups and permissions.
    """
    def create_parser(self, prog_name, subcommand, **kwargs):
        return super().create_parser(prog_name, subcommand,
            usage="%(prog)s workflow_file [-d] [-t] [--dry-run] [options]",
            **kwargs)

    def add_arguments(self, parser):
        parser.add_argument("workflow_file",
                            help="file typically [myapp]/workflow.toml")
        parser.add_argument("-d", "--doc", action='store_true',
                            required=False, help="generate a workflow documentation.")
        parser.add_argument("--dry-run", action='store_true',
                            required=False, help="don't actually write in db.")
        parser.add_argument("-t", "--model-template", action='store_true',
                            required=False, help="generate a workflow model template.")

    def handle(self, workflow_file, dry_run=False, *args, **options):
        if dry_run: print("-------- DRY-RUN ---------")
