from django.core.management.base import BaseCommand
from apps.machines.models import Status

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
    Status.objects.all().delete()

def create_status_machines():
    """Creates an address object combining different elements from the list"""
    names_statuses = [
        {"name": "Activo"},
        {"name": "Inactivo"},
        {"name": "En Mantenimiento"}
    ]
    
    for data in names_statuses:
        roles = Status.objects.create(**data)
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
    create_status_machines()
