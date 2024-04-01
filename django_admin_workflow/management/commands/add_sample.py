from django.core.management import BaseCommand

from django_admin_workflow.test import create_data


class Command(BaseCommand):
    help ="""
    Populate database with some sample data.
    Your app should override the create_data function typically in the tests.py module
    (see module vacation.tests)
"""
    def create_parser(self, prog_name, subcommand, **kwargs):
        return super().create_parser(prog_name, subcommand,
            usage="%(prog)s [-a [username=admin [passwd=username]]]  [options]",
            **kwargs)

    def add_arguments(self, parser):
        parser.add_argument("-a", "--admin", default=[], metavar="[user_name] [passwd]",
                            nargs="*", action="append",
                            required=False, help="add a superuser (defaults: admin admin)")
        parser.add_argument("--dry-run", action='store_true',
                            required=False, help="don't actually write in db.")

    def handle(self, admin, dry_run=False, *args, **options):
        create_data(create_su=len(admin) > 0, dry_run=dry_run)
