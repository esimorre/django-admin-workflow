import tomli
from django.contrib.auth.models import Group, Permission
from django.core.management import BaseCommand

from django_admin_workflow.management.commands._private import get_target_ctype, get_fields_model
from django_admin_workflow.models import RolePermission, Status


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
        self.not_dryrun = not dry_run
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
        if not workflow_file.endswith(".toml"):
            print("Only .toml files are accepted.")
            return
        self.fields_model = get_fields_model(ctype, joined=False)
        data = self._get_workflow_data(workflow_file)
        for gname in data:
            print("create or check group: ", gname)
            group = None
            if not dry_run:
                group, _ = Group.objects.get_or_create(name=gname)
            gcontent = data[gname]
            if 'creation':
                self._set_add_change_permission(ctype, group, add=True)

            self._check_fields(gcontent['creation']['fields'])
            self._check_fields(gcontent['creation']['readonly_fields'])

            for status, bloc_status  in gcontent.items():
                if status in ('creation', 'filter'): continue
                self._create_status(status)
                self._check_fields(bloc_status['fields'])
                self._check_fields(bloc_status['readonly_fields'])
                self._create_actions(ctype, bloc_status['actions'], group)


    def _get_workflow_data(self, file):

        dic = {}
        with open(file, "rb") as f:
            dic = tomli.load(f)
        return dic

    def _check_fields(self, items):
        items = set(items)
        if items.issubset(self.fields_model): return True
        print ("WARNING - Fields unknown: ", self.fields_model.difference(items))


    def _create_actions(self, ctype,  actions, group=None):
        for action in actions:
            if len(action) == 2:
                self._set_add_change_permission(ctype, group, change=True)

            if len(action) < 3: continue
            print("create role ", action[1], "for model:", ctype.model_class().__name__)
            if self.not_dryrun: RolePermission.objects.get_or_create(ctype=ctype, slug=action[0],
                                                 defaults={'verbose_name': action[1]})
            self._create_status(action[2])

    def _create_status(self, slug):
        verbose = slug[0].capitalize() + slug[1:]
        verbose = verbose.replace('_', ' ')
        print("create status ",slug, verbose)
        if self.not_dryrun:
            status, created = Status.objects.get_or_create(slug=slug, defaults={'verbose_name': verbose})

    def _set_add_change_permission(self, ctype, group, add=False, change=False):
        if add:      perm = "add_%s" % ctype.model
        elif change: perm = "change_%s" % ctype.model
        else: return
        p = Permission.objects.get(codename=perm, content_type=ctype)
        print(perm, "permission on group", group)
        if self.not_dryrun: group.permissions.add(p)