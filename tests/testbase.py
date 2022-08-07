import os
import sys
import unittest

from shotgun_api3.lib import mockgun


class BaseShotGridTest(unittest.TestCase):
    """
    Base Test Class to setup Mockgun.
    """
    sg = None

    @classmethod
    def setUpClass(cls):
        resources_dir = os.path.join(os.path.dirname(__file__), 'resources')

        mockgun_schema_dir = os.path.join(resources_dir, 'mockgun_schemas',
                                          'py{}'.format(sys.version_info.major))
        mockgun.Shotgun.set_schema_paths(os.path.join(mockgun_schema_dir, 'schema.db'),
                                         os.path.join(mockgun_schema_dir, 'entity_schema.db'))
        cls.sg = mockgun.Shotgun(base_url='https://test.shotgunstudio.com',
                                 script_name='Unittest User',
                                 api_key='$ome_password')
