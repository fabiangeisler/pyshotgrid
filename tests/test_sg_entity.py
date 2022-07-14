#!/usr/bin/env python

"""Tests for `pyshotgrid` package."""
import sys
if sys.version_info.major == 2:
    # noinspection PyPackageRequirements,PyUnresolvedReferences
    import mock
else:
    from unittest import mock

from shotgun_api3.lib import mockgun

from .testbase import BaseShotGridTest

import pyshotgrid as pysg


class TestSGEntity(BaseShotGridTest):
    """Tests for `pyshotgrid` package."""

    @classmethod
    def setUpClass(cls):
        super(TestSGEntity, cls).setUpClass()

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

    def test_string_representation(self):
        sg_entity = pysg.SGEntity(self.sg, 'Project', 1)

        self.assertEqual('SGEntity - Type: Project - ID: 1 - '
                         'URL: https://test.shotgunstudio.com/detail/Project/1',
                         str(sg_entity))

    def test_query_field_dict_notation(self):
        sg_entity = pysg.SGEntity(self.sg, 'Project', 1)

        self.assertEqual('tp', sg_entity['tank_name'].get())

    def test_update_field_dict_notation(self):
        sg_entity = pysg.SGEntity(self.sg, 'Project', 1)

        sg_entity['code'].set('bar-baz')

        self.assertEqual('bar-baz', sg_entity['code'].get())

        # cleanup
        sg_entity['code'].set('Test project')

    def test_convert_to_dict(self):
        # published files to query publish form paths.
        sg_publish = self.sg.create('PublishedFile', {'code': 'delete_me'})
        sg_entity = pysg.SGEntity(self.sg, sg_publish['type'], sg_publish['id'])

        sg_entity.delete()

        self.assertEqual([],
                         self.sg.find(sg_publish['type'], [['id', 'is', sg_publish['id']]]))

    def test_delete(self):
        sg_entity = pysg.SGEntity(self.sg, 'LocalStorage', 1)

        self.assertEqual({'id': 1, 'type': 'LocalStorage'},
                         sg_entity.to_dict())

    def test_iter_fields(self):
        sg_entity = pysg.SGEntity(self.sg, 'LocalStorage', 1)

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
            result = set(sg_entity.all_field_values().items())

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

    def test_shotgun_url(self):
        sg_entity = pysg.SGEntity(self.sg, 'Project', 1)

        self.assertEqual('https://test.shotgunstudio.com/detail/Project/1',
                         sg_entity.url)
