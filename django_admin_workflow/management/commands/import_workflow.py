import tomli
from django.core.management import BaseCommand

from django_admin_workflow.management.commands._private import get_target_ctype


class Command(BaseCommand):

    help = """import a workflow definition file (see gen_workflow_template) to generate objects in db.
    This command generates groups and permissions.
    """
    def create_parser(self, prog_name, subcommand, **kwargs):
        return super().create_parser(prog_name, subcommand,
            usage="%(prog)s workflow_file [-m app_label.model_name] [-d] [--dry-run] [options]",
            **kwargs)

    def add_arguments(self, parser):
        parser.add_argument("workflow_file",
                            help="file typically [myapp]/workflow.toml")
        parser.add_argument("-m", "--model", metavar="app_label.model", nargs=1,
                            required=False, help="workflow model (based on BaseStateModel)")
        parser.add_argument("-d", "--doc", action='store_true',
                            required=False, help="generate a workflow documentation.")
        parser.add_argument("--dry-run", action='store_true',
                            required=False, help="don't actually write in db.")

    def handle(self, workflow_file, model, dry_run=False, *args, **options):
        if dry_run: print("-------- DRY-RUN ---------")
        data = self._get_workflow_data(workflow_file)
        ctype, wf_ready, explicit, nb_wf = get_target_ctype(model)
        print(data)
        print(ctype, wf_ready, explicit, nb_wf)
        if not ctype:
            print("No workflow model detected or simple model mentioned.")
            return
        if nb_wf > 1:
            print("Several workflow model detected. please use -m option.")
            return


    def _get_workflow_data(self, file):
        dic = {}
        with open(file, "rb") as f:
            dic = tomli.load(f)
        return dic
