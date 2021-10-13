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


class TestPyshotgrid(BaseTestShotgunLib):
    """Tests for `pyshotgrid` package."""

    @classmethod
    def setUpClass(cls):
        super(TestPyshotgrid, cls).setUpClass()

        # Shotgun test project
        cls.sg_project = cls.sg.create('Project', {'code': 'Test Project',
                                                   'tank_name': 'tp'})
        # LocalStorages needed for Operating system independent paths
        local_storage = cls.sg.create('LocalStorage', {'code': 'primary',
                                                       'mac_path': '/Volumes/projects',
                                                       'windows_path': 'P:\\',
                                                       'linux_path': '/mnt/projects'})

        # published files to query publish form paths.
        cls.sg_publish = cls.sg.create(
            'PublishedFile',
            {
                'code': '0010_v001.%04d.exr',
                'path_cache': 'tp/sequences/0010_v001.%04d.exr',
                'path_cache_storage': local_storage
            })

    def test_ShotGridEntity_string_representation(self):
        sg_entity = pysg.ShotGridEntity(self.sg, 'Project', 1)

        self.assertEqual('ShotGridEntity  Type: Project  ID: 1', str(sg_entity))

    def test_ShotGridEntity_query_field_dot_notation(self):
        sg_entity = pysg.ShotGridEntity(self.sg, 'Project', 1)

        self.assertEqual('tp', sg_entity.tank_name)

    def test_ShotGridEntity_query_field_dict_notation(self):
        sg_entity = pysg.ShotGridEntity(self.sg, 'Project', 1)

        self.assertEqual('tp', sg_entity['tank_name'])

    def test_ShotGridEntity_update_field_dot_notation(self):
        sg_entity = pysg.ShotGridEntity(self.sg, 'Project', 1)

        sg_entity.code = 'foobar'

        self.assertEqual('foobar', sg_entity.code)

        # cleanup
        sg_entity.code = 'Test project'

    def test_ShotGridEntity_update_field_dict_notation(self):
        sg_entity = pysg.ShotGridEntity(self.sg, 'Project', 1)

        sg_entity['code'] = 'bar-baz'

        self.assertEqual('bar-baz', sg_entity['code'])

        # cleanup
        sg_entity['code'] = 'Test project'

    def test_ShotGridEntity_len_of_fields(self):
        sg_entity = pysg.ShotGridEntity(self.sg, 'Project', 1)

        self.assertEqual(67, len(sg_entity))

    def test_ShotGridEntity_convert_to_dict(self):
        sg_entity = pysg.ShotGridEntity(self.sg, 'LocalStorage', 1)

        self.assertEqual({'cached_display_name': None,
                          'code': 'primary',
                          'created_at': None,
                          'created_by': None,
                          'description': None,
                          'id': 1,
                          'linux_path': '/mnt/projects',
                          'mac_path': '/Volumes/projects',
                          'type': 'LocalStorage',
                          'updated_at': None,
                          'updated_by': None,
                          'uuid': None,
                          'windows_path': 'P:\\'},
                         dict(sg_entity))

    def test_ShotGridEntity_iter_fields(self):
        sg_entity = pysg.ShotGridEntity(self.sg, 'LocalStorage', 1)

        self.assertEqual({('linux_path', '/mnt/projects'),
                          ('type', 'LocalStorage'),
                          ('id', 1),
                          ('description', None),
                          ('cached_display_name', None),
                          ('mac_path', '/Volumes/projects'),
                          ('created_by', None),
                          ('updated_by', None),
                          ('created_at', None),
                          ('windows_path', 'P:\\'),
                          ('uuid', None),
                          ('code', 'primary'),
                          ('updated_at', None)},
                         set(sg_entity.items()))

    def test_ShotGridEntity_shotgun_url(self):
        sg_entity = pysg.ShotGridEntity(self.sg, 'Project', 1)

        self.assertEqual('https://test.shotgunstudio.com/detail/Project/1',
                         sg_entity.shotgrid_url)
