from django.core.management.base import BaseCommand
from apps.roles.models import Role

""" Clear all data and creates addresses """
MODE_REFRESH = 'refresh'

""" Clear all data and do not create any object """
MODE_CLEAR = 'clear'

class Command(BaseCommand):
    help = "seed database for testing and development."
    def add_arguments(self, parser):
        parser.add_argument('--mode', type=str, help="Mode")

    def handle(self, *args, **options):
        self.stdout.write('seeding data...')
        run_seed(self, options['mode'])
        self.stdout.write('done.')

def clear_data():
    """Deletes all the table data"""
    Role.objects.all().delete()

def create_roles():
    """Creates an address object combining different elements from the list"""
    names_role = [
        {"name": "Admin"},
        {"name": "Guest"},
        {"name": "Visualizer"},
        {"name": "Technical"},
        {"name": "Provider"}
    ]
    
    for data in names_role:
        roles = Role.objects.create(**data)
        roles.save()
    
def run_seed(self, mode):
    """ Seed database based on mode

    :param mode: refresh / clear 
    :return:
    """
    # Clear data from tables
    clear_data()
    if mode == MODE_CLEAR:
        return

    # Creating roles
    create_roles()
