from time import sleep

from django.core.management import BaseCommand
from django_admin_workflow.management.commands._private import get_target_ctype, get_fields_model


class Command(BaseCommand):
    help = "Run executor(s) typically with cron"
    def create_parser(self, prog_name, subcommand, **kwargs):
        return super().create_parser(prog_name, subcommand,
            usage="%(prog)s -e app_label.executor_name [-m app_label.model_name ...]\
            \n                  [-p space] [-s status] [-c nb_seconds] [options]",
            **kwargs)

    def add_arguments(self, parser):
        parser.add_argument("-e", "--executors", metavar="app_label.executor_name", nargs="*",
                            required=True, help="executor(s) selection")
        parser.add_argument("-m", "--models", metavar="app_label.model_name", nargs="*",
                            required=False, help="model(s) to process")
        parser.add_argument("-p", "--spaces", nargs="*",
                            required=False, help="filter on space")
        parser.add_argument("-s", "--status", nargs=1,
                            required=False, help="filter on status")
        parser.add_argument("-c", "--cron-simul", metavar="period", nargs=1, type=int,
                            required=False, help="interactive mode with a period in seconds")

    def handle(self, executors, models, status, spaces, cron_simul, *args, **options):
        ctype_model, wf_ready, _, _ = get_target_ctype(models)
        if not wf_ready:
            print ("error model", ctype_model)
            return
        ctype_exe, wf_ready, _, _ = get_target_ctype(executors)
        if wf_ready:
            print ("error executor", ctype_exe)
            return

        if cron_simul:
            while True:
                self._run(ctype_exe, ctype_model, status, spaces)
                sleep(cron_simul[0])
        else:
            self._run(ctype_exe, ctype_model, status, spaces)

    def _run(self, ctype_exe, ctype_model, status, spaces):
        print("run",ctype_exe, ctype_model, status, spaces)




