from django.core.management import BaseCommand


_template = """
[GROUP_NAME]
    # filter on space
    filter = "lambda q, user_space, user: q.filter(space=user_space)"

    # fields access on creation
    [GROUP_NAME.creation]
    fields =  [FIELDS_LIST]
    readonly_fields = [FIELDS_LIST]

    # The 'DRAFT' status is the default for all workflow models
    [GROUP_NAME.DRAFT]
    perms = [PERMISSION_LIST]
    fields =  [FIELDS_LIST]
    readonly_fields = [FIELDS_LIST]
    actions = [ [ACTION_CODE,    ACTION_VERBOSE],
                [ACTION_CODE2,   ACTION_VERBOSE2,   STATUS_TARGET]]

#### Add others status. This is an example for the DRAFT status
#    [clients.DRAFT]
#    perms = ["can_submit"]
#    fields =  ['name', 'contact', 'status']
#    readonly_fields = ['status']
#    actions = [ ["save",     "Save"],
#                ["submit",   "Submit", "submited"],
#                ["cancel",   "Cancel",   "canceled"]]

#### Add others [GROUP_NAME] sections
"""

class Command(BaseCommand):
    help = "Generate a .toml workflow template file on stdout"
    def create_parser(self, prog_name, subcommand, **kwargs):
        return super().create_parser(prog_name, subcommand,
            usage="%(prog)s [-m app_label.model_name] [options] [ > workflow.toml ]",
            **kwargs)

    def add_arguments(self, parser):
        parser.add_argument("-m", "--model", metavar="[app_label].[model]",
                            required=False, help="workflow model (based on BaseStateModel)")
    def handle(self, *args, **options):
        print(_template)
        msg = """
# 1. Put this in a file ie. named 'workflow.toml' in your app directory
# 2. Edit this file with real values
# 3. fill the "access_rules" field of the ModelAdmin registered for the workflow model:
#      @admin.register(MyTestModel)
#      class MyTestModelAdmin(WorkflowModelAdmin):
#          access_rules = get_workflow_data(__file__, file_data="workflow.toml")
        """
        print(msg)
