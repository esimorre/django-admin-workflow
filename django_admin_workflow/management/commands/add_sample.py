from django.core.management import BaseCommand


class Command(BaseCommand):
    help = "Populate database with some sample data"
    def create_parser(self, prog_name, subcommand, **kwargs):
        return super().create_parser(prog_name, subcommand,
            usage="%(prog)s [-a [username=admin [passwd=username]]]  [options]",
            **kwargs)

    def add_arguments(self, parser):
        parser.add_argument("-a", "--admin", default="admin", metavar="[user_name] [passwd]",
                            required=False, help="add a superuser (defaults: admin admin)")
        parser.add_argument("--dry-run", action='store_true',
                            required=False, help="don't actually write in db.")

    def handle(self, *args, **options):
        print("TODO")
