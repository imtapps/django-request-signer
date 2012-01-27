from cStringIO import StringIO

from lettuce import before, after, world
from django.db import connection
from django.core.management import call_command
from south.management.commands import patch_for_test_db_setup

@before.all
def setup_test_database():
    patch_for_test_db_setup()
    world.test_database_name = connection.creation.create_test_db(verbosity=0, autoclobber=True)

@before.each_scenario
def clean_db(scenario):
    call_command('flush', interactive=False, stderr=StringIO())

@after.all
def teardown_test_database(scenario):
    connection.creation.destroy_test_db(world.test_database_name, verbosity=0)
