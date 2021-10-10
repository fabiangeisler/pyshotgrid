#!/usr/bin/env python

"""Tests for `pyshotgrid` package."""
import os
import sys
import unittest

from shotgun_api3.lib import mockgun

import pyshotgrid as pysg


class BaseTestShotgunLib(unittest.TestCase):
    """
    Base Test Class to setup Mockgun.
    """
    shotgun = None

    @classmethod
    def setUpClass(cls):
        resources_dir = os.path.join(os.path.dirname(__file__), 'resources')

        mockgun_schema_dir = os.path.join(resources_dir, 'mockgun_schemas',
                                          'py{}'.format(sys.version_info.major))
        mockgun.Shotgun.set_schema_paths(os.path.join(mockgun_schema_dir, 'schema.db'),
                                         os.path.join(mockgun_schema_dir, 'entity_schema.db'))
        cls.shotgun = mockgun.Shotgun(base_url='https://automatik-vfx.shotgunstudio.com',
                                      script_name='Unittest User',
                                      api_key='$ome_password')


class TestPyshotgrid(BaseTestShotgunLib):
    """Tests for `pyshotgrid` package."""

    @classmethod
    def setUpClass(cls):
        super(TestPyshotgrid, cls).setUpClass()

        # Shotgun test project
        cls.sg_project = cls.shotgun.create('Project', {'code': 'atk_template_project',
                                                        'tank_name': 'atk_template_project'})
        # LocalStorages needed for Operating system independent paths
        local_storage = cls.shotgun.create('LocalStorage', {'code': 'primary',
                                                            'mac_path': '/Volumes/projects',
                                                            'windows_path': 'P:\\',
                                                            'linux_path': '/mnt/projects'})

        # published files to query publish form paths.
        cls.sg_publish = cls.shotgun.create(
            'PublishedFile',
            {
                'code': '019_0010_plate_BG2_v001.%04d.exr',
                'path_cache': 'atk_template_project/sequences/'
                              'ep003_019/019_0010/plates/BG2/v001/3414x2198/019_0010_plate_BG2_v001.%04d.exr',
                'path_cache_storage': local_storage
            })

    def test_000_something(self):
        """Test something."""
