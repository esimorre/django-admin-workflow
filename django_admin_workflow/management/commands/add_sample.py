from django.core.management import BaseCommand


class Command(BaseCommand):
    help = "Populate database with some sample data"

    def add_arguments(self, parser):
        parser._actions = []
        parser.add_argument("-a", "--admin", default="admin", metavar="[admin] [admin]",
                            required=False, help="add a superuser")

    def handle(self, *args, **options):
        print("TODO")
        self.stdout.write(self.style.WARNING("WARNING..."))
        self.stdout.write(self.style.SUCCESS("SUCCESS..."))
        self.stdout.write(self.style.ERROR("ERROR..."))
