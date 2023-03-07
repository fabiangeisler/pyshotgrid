#!/usr/bin/env python

"""Tests for `pyshotgrid` package."""
import sys

if sys.version_info.major == 2:
    # noinspection PyPackageRequirements,PyUnresolvedReferences
    import mock
else:
    from unittest import mock

from shotgun_api3.lib import mockgun

import pyshotgrid as pysg

from .testbase import BaseShotGridTest


class TestSGEntity(BaseShotGridTest):
    """Tests for `pyshotgrid` package."""

    @classmethod
    def setUpClass(cls):
        super(TestSGEntity, cls).setUpClass()

        cls.add_default_entities()

    def test_string_representation(self):
        sg_entity = pysg.SGEntity(self.sg, "Project", 1)

        self.assertEqual(
            "SGEntity - Type: Project - ID: 1 - "
            "URL: https://test.shotgunstudio.com/detail/Project/1",
            str(sg_entity),
        )

    def test_query_field_dict_notation(self):
        sg_entity = pysg.SGEntity(self.sg, "Project", 1)

        self.assertEqual("tpa", sg_entity["tank_name"].get())

    def test_get(self):
        sg_entity = pysg.SGEntity(self.sg, "Project", 1)

        self.assertEqual(
            {"name": "Test Project A", "tank_name": "tpa"},
            sg_entity.get(["name", "tank_name"]),
        )

    def test_name(self):
        sg_project = pysg.new_entity(self.sg, "Project", 1)
        sg_task = pysg.new_entity(self.sg, "Task", 1)
        sg_asset = pysg.new_entity(self.sg, "Asset", 1)

        result_project_name_field = sg_project.name
        result_task_name_field = sg_task.name
        result_asset_name_field = sg_asset.name

        self.assertEqual("name", result_project_name_field.name)
        self.assertEqual("content", result_task_name_field.name)
        self.assertEqual("code", result_asset_name_field.name)

    def test_name__errors_when_no_name_field_present(self):
        sg_entity = pysg.new_entity(self.sg, "Note", 1)

        with self.assertRaises(RuntimeError):
            _ = sg_entity.name

    # FIXME Mockgun.update is missing the "multi_entity_update_modes" parameter. We need to patch it
    # FIXME to make this test work.
    # def test_set(self):
    #     sg_entity = pysg.SGEntity(self.sg, 'Project', 1)
    #     def patched_update(entity_type, entity_id, data, multi_entity_update_modes=None):
    #         self.sg.update(entity_type, entity_id, data)
    #
    #     with mock.patch.object(mockgun.Shotgun, "update", new_callable=patched_update):
    #         sg_entity.set({'code': 'Test Name', 'tank_name': 'tn'})
    #
    #     self.assertEqual({'code': 'Test Name', 'tank_name': 'tn'},
    #                      sg_entity.get(['code', 'tank_name']))
    #     # Cleanup
    #     sg_entity.set({'code': 'Test Project', 'tank_name': 'tp'})

    def test_update_field_dict_notation(self):
        sg_entity = pysg.SGEntity(self.sg, "Project", 1)
        sg_entity["code"].set("bar-baz")

        self.assertEqual("bar-baz", sg_entity["code"].get())

        # cleanup
        sg_entity["code"].set("Test project")

    def test_convert_to_dict(self):
        # published files to query publish form paths.
        sg_publish = self.sg.create("PublishedFile", {"code": "delete_me"})
        sg_entity = pysg.SGEntity(self.sg, sg_publish["type"], sg_publish["id"])

        sg_entity.delete()

        self.assertEqual(
            [], self.sg.find(sg_publish["type"], [["id", "is", sg_publish["id"]]])
        )

    def test_delete(self):
        sg_entity = pysg.SGEntity(self.sg, "LocalStorage", 1)

        self.assertEqual({"id": 1, "type": "LocalStorage"}, sg_entity.to_dict())

    def test_site(self):
        sg_entity = pysg.SGEntity(self.sg, "LocalStorage", 1)

        self.assertIsInstance(sg_entity.site, pysg.SGSite)

    def test_iter_all_field_values(self):
        sg_entity = pysg.SGEntity(self.sg, "LocalStorage", 1)

        # Mock Mockgun.schema_field_read - the "project_entity" arg is missing in Mockgun.
        with mock.patch.object(
            mockgun.Shotgun,
            "schema_field_read",
            return_value={
                "linux_path": {"visible": {"value": True}},
                "type": {"visible": {"value": True}},
                "id": {"visible": {"value": True}},
                "description": {"visible": {"value": True}},
                "cached_display_name": {"visible": {"value": True}},
                "mac_path": {"visible": {"value": True}},
                "created_at": {"visible": {"value": True}},
                "created_by": {"visible": {"value": True}},
                "windows_path": {"visible": {"value": True}},
                "uuid": {"visible": {"value": True}},
                "code": {"visible": {"value": True}},
                "updated_at": {"visible": {"value": True}},
                "updated_by": {"visible": {"value": True}},
            },
        ):
            result = set(sg_entity.all_field_values().items())

        self.assertEqual(
            {
                ("linux_path", "/mnt/projects"),
                ("type", "LocalStorage"),
                ("id", 1),
                ("description", None),
                ("cached_display_name", None),
                ("mac_path", "/Volumes/projects"),
                ("created_by", None),
                ("updated_by", None),
                ("created_at", None),
                ("windows_path", "P:\\"),
                ("uuid", None),
                ("code", "primary"),
                ("updated_at", None),
            },
            result,
        )

    def test_fields(self):
        sg_entity = pysg.SGEntity(self.sg, "LocalStorage", 1)

        # Mock Mockgun.schema_field_read - the "project_entity" arg is missing in Mockgun.
        with mock.patch.object(
            mockgun.Shotgun,
            "schema_field_read",
            return_value={
                "linux_path": {"visible": {"value": True}},
                "type": {"visible": {"value": True}},
                "id": {"visible": {"value": True}},
                "description": {"visible": {"value": True}},
                "cached_display_name": {"visible": {"value": True}},
                "mac_path": {"visible": {"value": True}},
                "created_at": {"visible": {"value": True}},
                "created_by": {"visible": {"value": True}},
                "windows_path": {"visible": {"value": True}},
                "uuid": {"visible": {"value": True}},
                "code": {"visible": {"value": True}},
                "updated_at": {"visible": {"value": True}},
                "updated_by": {"visible": {"value": True}},
            },
        ):
            result = sg_entity.fields()

        self.assertEqual(
            {
                "linux_path",
                "type",
                "id",
                "description",
                "cached_display_name",
                "mac_path",
                "created_by",
                "updated_by",
                "created_at",
                "windows_path",
                "uuid",
                "code",
                "updated_at",
            },
            {field.name for field in result},
        )
        self.assertTrue(all([isinstance(field, pysg.Field) for field in result]))

    def test_shotgun_url(self):
        sg_entity = pysg.SGEntity(self.sg, "Project", 1)

        self.assertEqual(
            "https://test.shotgunstudio.com/detail/Project/1", sg_entity.url
        )

    def test_entity_display_name(self):
        sg_entity = pysg.SGEntity(self.sg, "CustomEntity01", 1)

        self.assertEqual("Sprint", sg_entity.entity_display_name)

    def test_schema(self):
        sg_entity = pysg.SGEntity(self.sg, "Project", 1)

        self.assertEqual(
            {
                "name": {"editable": False, "value": "Project"},
                "visible": {"editable": False, "value": True},
            },
            sg_entity.schema(),
        )

    def test_field_schemas(self):
        sg_entity = pysg.SGEntity(self.sg, "Project", 1)

        result = sg_entity.field_schemas()

        self.assertEqual("Tank Name", result["tank_name"].display_name)
        self.assertEqual(67, len(result))

    def test_compare_entities(self):
        sg_entity_a = pysg.SGEntity(self.sg, "Project", 1)
        sg_entity_b = pysg.sg_default_entities.SGProject(self.sg, 1)

        result = sg_entity_a == sg_entity_b

        self.assertTrue(result)

    def test_compare_entities__ids_dont_match(self):
        sg_entity_a = pysg.SGEntity(self.sg, "Project", 1)
        sg_entity_b = pysg.SGEntity(self.sg, "Project", 2)

        result = sg_entity_a != sg_entity_b

        self.assertTrue(result)

    def test_compare_entities__entity_types_dont_match(self):
        sg_entity_a = pysg.SGEntity(self.sg, "Project", 1)
        sg_entity_b = pysg.SGEntity(self.sg, "Version", 1)

        result = sg_entity_a != sg_entity_b

        self.assertTrue(result)

    def test_compare_entities__sg_instances_dont_match(self):
        sg_entity_a = pysg.SGEntity(self.sg, "Project", 1)
        other_sg = mockgun.Shotgun(
            base_url="https://other.shotgunstudio.com",
            script_name="Unittest User",
            api_key="$ome_password",
        )
        sg_entity_b = pysg.SGEntity(other_sg, "Project", 1)

        result = sg_entity_a != sg_entity_b

        self.assertTrue(result)
