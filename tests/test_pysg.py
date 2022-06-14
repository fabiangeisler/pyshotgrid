#!/usr/bin/env python

"""Tests for `pyshotgrid` package."""
import os
import sys
import unittest
if sys.version_info.major == 2:
    # noinspection PyPackageRequirements,PyUnresolvedReferences
    import mock
else:
    from unittest import mock

from shotgun_api3.lib import mockgun

import pyshotgrid


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


class TestPySG(BaseTestShotgunLib):
    """Tests for `pyshotgrid` package."""

    @classmethod
    def setUpClass(cls):
        super(TestPySG, cls).setUpClass()

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
        sg_entity = pyshotgrid.ShotGridEntity(self.sg, 'Project', 1)

        self.assertEqual('ShotGridEntity - Type: Project - ID: 1 - '
                         'URL: https://test.shotgunstudio.com/detail/Project/1',
                         str(sg_entity))

    def test_ShotGridEntity_query_field_dict_notation(self):
        sg_entity = pyshotgrid.ShotGridEntity(self.sg, 'Project', 1)

        self.assertEqual('tp', sg_entity['tank_name'])

    def test_ShotGridEntity_update_field_dict_notation(self):
        sg_entity = pyshotgrid.ShotGridEntity(self.sg, 'Project', 1)

        sg_entity['code'] = 'bar-baz'

        self.assertEqual('bar-baz', sg_entity['code'])

        # cleanup
        sg_entity['code'] = 'Test project'

    def test_ShotGridEntity_convert_to_dict(self):
        sg_entity = pyshotgrid.ShotGridEntity(self.sg, 'LocalStorage', 1)

        self.assertEqual({'id': 1, 'type': 'LocalStorage'},
                         sg_entity.to_dict())

    def test_ShotGridEntity_iter_fields(self):
        sg_entity = pyshotgrid.ShotGridEntity(self.sg, 'LocalStorage', 1)

        # Mock Mockgun.schema_field_read - the "project_entity" arg is missing in Mockgun.
        with mock.patch.object(mockgun.Shotgun, "schema_field_read",
                               return_value={
                'linux_path': {'visible': {'value': True}},
                'type': {'visible': {'value': True}},
                'id': {'visible': {'value': True}},
                'description': {'visible': {'value': True}},
                'cached_display_name': {'visible': {'value': True}},
                'mac_path': {'visible': {'value': True}},
                'created_at': {'visible': {'value': True}},
                'created_by': {'visible': {'value': True}},
                'windows_path': {'visible': {'value': True}},
                'uuid': {'visible': {'value': True}},
                'code': {'visible': {'value': True}},
                'updated_at': {'visible': {'value': True}},
                'updated_by': {'visible': {'value': True}},
                                        }):
            result = set(sg_entity.all_fields().items())

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
                         result)

    def test_ShotGridEntity_shotgun_url(self):
        sg_entity = pyshotgrid.ShotGridEntity(self.sg, 'Project', 1)

        self.assertEqual('https://test.shotgunstudio.com/detail/Project/1',
                         sg_entity.url)
