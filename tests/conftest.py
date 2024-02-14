import datetime
import os
import random
import sys

import pytest
from shotgun_api3.lib import mockgun


@pytest.fixture(params=(True, False))
def use_shotgun_api3_from_sgtk(request, monkeypatch):
    """
    This is a parametrized fixture which will run any test that requests it once against
    the "regular" pip installed "shotgun_api3" and another time against
    the vendor-ed "shotgun_api3" in SGTk to ensure the test works in both scenarios.
    """
    if request.param:
        # noinspection PyTypeChecker
        monkeypatch.setitem(sys.modules, "shotgun_api3", None)
    else:
        # noinspection PyTypeChecker
        monkeypatch.setitem(sys.modules, "tank_vendor.shotgun_api3", None)
    return request.param


@pytest.fixture()
def sg():
    """
    This fixture sets up a (mockgun.)Shotgun instance with a few useful test entries
    to test against.
    """
    resources_dir = os.path.join(os.path.dirname(__file__), "resources")

    mockgun_schema_dir = os.path.join(resources_dir, "mockgun_schemas")
    mockgun.Shotgun.set_schema_paths(
        os.path.join(mockgun_schema_dir, "schema.db"),
        os.path.join(mockgun_schema_dir, "entity_schema.db"),
    )
    sg = mockgun.Shotgun(
        base_url="https://test.shotgunstudio.com",
        script_name="Unittest User",
        api_key="$ome_password",
    )

    add_default_entities(sg)

    # mockgun.Shotgun does not have a function "download_attachment()" so
    # we mock it for the tests.
    def mock_download_attachment(self, attachment, file_path):
        return {"type": "Attachment", "id": random.randint(1, 1000)}

    mockgun.Shotgun.download_attachment = mock_download_attachment

    # mockgun.Shotgun.update is missing the "multi_entity_update_modes" parameter.
    # We need to patch it to make the tests work.
    def patched_update(self, entity_type, entity_id, data, multi_entity_update_modes=None):
        self._validate_entity_type(entity_type)
        if "image" not in data:
            self._validate_entity_data(entity_type, data)
        self._validate_entity_exists(entity_type, entity_id)

        row = self._db[entity_type][entity_id]

        if multi_entity_update_modes is not None:
            new_data = {}
            for field, value in data.items():
                mode = multi_entity_update_modes.get(field, "set")

                if mode == "add":
                    sg_entity = sg.find_one(entity_type, [["id", "is", entity_id]], [field])
                    tmp_result = sg_entity[field]
                    for entity in value:
                        if entity not in tmp_result:
                            tmp_result.append(entity)
                    new_data[field] = tmp_result

                elif mode == "remove":
                    sg_entity = sg.find_one(entity_type, [["id", "is", entity_id]], [field])
                    tmp_result = sg_entity[field]
                    for entity in value:
                        if entity in tmp_result:
                            tmp_result.remove(entity)
                    new_data[field] = tmp_result

                else:  # "set"
                    new_data[field] = value
            data = new_data

        self._update_row(entity_type, row, data)

        return [
            dict(
                (field, item)
                for field, item in row.items()
                if field in data or field in ("type", "id")
            )
        ]

    mockgun.Shotgun.update = patched_update

    # Patching the mockgun.Shotgun.find method because it is missing 2 arguments
    # "include_archived_projects" and "additional_filter_presets".
    def patched_find(
        self,
        entity_type,
        filters,
        fields=None,
        order=None,
        filter_operator=None,
        limit=0,
        retired_only=False,
        page=0,
        include_archived_projects=True,
        additional_filter_presets=None,
    ):
        if not include_archived_projects:
            raise NotImplementedError(
                'The logic for "include_archived_projects" is not implemented.'
            )

        if additional_filter_presets is not None:
            raise NotImplementedError(
                'The logic for "additional_filter_presets" is not implemented.'
            )

        self.finds += 1

        self._validate_entity_type(entity_type)
        # do not validate custom fields - this makes it hard to mock up a field quickly
        # self._validate_entity_fields(entity_type, fields)

        if isinstance(filters, dict):
            # complex filter style!
            # {'conditions': [{'path': 'id', 'relation': 'is', 'values': [1]}],
            #                 'logical_operator': 'and'}

            resolved_filters = []
            for f in filters["conditions"]:
                if f["path"].startswith("$FROM$"):
                    # special $FROM$Task.step.entity syntax
                    # skip this for now
                    continue

                if len(f["values"]) != 1:
                    # {'path': 'id', 'relation': 'in', 'values': [1,2,3]} --> ["id", "in", [1,2,3]]
                    resolved_filters.append([f["path"], f["relation"], f["values"]])
                else:
                    # {'path': 'id', 'relation': 'is', 'values': [3]} --> ["id", "is", 3]
                    resolved_filters.append([f["path"], f["relation"], f["values"][0]])

        else:
            # traditional style sg filters
            resolved_filters = filters

        results = [
            # Apply the filters for every single entities for the given entity type.
            row
            for row in self._db[entity_type].values()
            if self._row_matches_filters(
                entity_type, row, resolved_filters, filter_operator, retired_only
            )
        ]

        # handle the ordering of the recordset
        if order:
            # order: [{"field_name": "code", "direction": "asc"}, ... ]
            for order_entry in order:
                if "field_name" not in order_entry:
                    raise ValueError(
                        "Order clauses must be list of dicts with keys "
                        "'field_name' and 'direction'!"
                    )

                order_field = order_entry["field_name"]
                if order_entry["direction"] == "asc":
                    desc_order = False
                elif order_entry["direction"] == "desc":
                    desc_order = True
                else:
                    raise ValueError("Unknown ordering direction")

                results = sorted(results, key=lambda k: k[order_field], reverse=desc_order)

        if fields is None:
            fields = {"type", "id"}
        else:
            fields = set(fields) | {"type", "id"}

        # get the values requested
        val = [
            dict((field, self._get_field_from_row(entity_type, row, field)) for field in fields)
            for row in results
        ]

        return val

    mockgun.Shotgun.find = patched_find

    return sg


def add_default_entities(sg):
    # HumanUsers
    person_a = sg.create(
        "HumanUser",
        {
            "firstname": "Alice",
            "lastname": "Alpha",
            "name": "Alice Alpha",
            "login": "alice.alpha",
            "email": "alice@company.com",
        },
    )
    person_b = sg.create(
        "HumanUser",
        {
            "firstname": "Bob",
            "lastname": "Beta",
            "name": "Bob Beta",
            "login": "bob.beta",
            "email": "bob@company.com",
        },
    )
    person_c = sg.create(
        "HumanUser",
        {
            "firstname": "Carol",
            "lastname": "Clown",
            "name": "Carol Clown",
            "login": "carol.clown",
            "email": "carol@company.com",
        },
    )
    sg.create(
        "HumanUser",
        {
            "firstname": "Dan",
            "lastname": "Deactivated",
            "name": "Dan Deactivated",
            "login": "dan.deactivated",
            "email": "dan@company.com",
            "sg_status_list": "dis",
        },
    )

    # LocalStorages
    local_storage = sg.create(
        "LocalStorage",
        {
            "code": "primary",
            "mac_path": "/Volumes/projects",
            "windows_path": "P:\\",
            "linux_path": "/mnt/projects",
        },
    )

    # Pipeline Steps
    pipeline_step_cmp = sg.create("Step", {"code": "Compositing", "short_name": "CMP"})
    pipeline_step_lgt = sg.create("Step", {"code": "Lighting", "short_name": "LGT"})
    pipeline_step_mdl = sg.create("Step", {"code": "Modeling", "short_name": "MDL"})

    # Projects
    project_a = sg.create(
        "Project",
        {
            "name": "Test Project A",
            "tank_name": "tpa",
            "users": [person_a, person_b, person_c],
            "is_template": False,
        },
    )
    project_b = sg.create(
        "Project",
        {
            "name": "Test Project B",
            "tank_name": "tpb",
            "users": [person_a, person_b, person_c],
            "is_template": False,
        },
    )

    sg.update("HumanUser", 1, {"projects": [project_a, project_b]})
    sg.update("HumanUser", 2, {"projects": [project_a, project_b]})
    sg.update("HumanUser", 3, {"projects": [project_a, project_b]})
    sg.update("HumanUser", 4, {"projects": [project_a, project_b]})

    # Assets
    asset_tree_a = sg.create("Asset", {"code": "Tree", "project": project_a})
    asset_car_a = sg.create("Asset", {"code": "CarA", "project": project_a})
    sg.create("Asset", {"code": "CarB", "project": project_a})

    # Sequences
    sq111 = sg.create("Sequence", {"code": "sq111", "project": project_a})
    sq222 = sg.create("Sequence", {"code": "sq222", "project": project_a})

    # Shots
    shot_a = sg.create("Shot", {"code": "sq111_sh1111", "project": project_a, "sg_sequence": sq111})
    shot_b = sg.create("Shot", {"code": "sq111_sh2222", "project": project_a, "sg_sequence": sq111})
    sg.create("Shot", {"code": "sq222_sh3333", "project": project_a, "sg_sequence": sq222})
    sg.create("Shot", {"code": "sq222_sh4444", "project": project_a, "sg_sequence": sq222})

    # Tasks
    task_cmp_a = sg.create(
        "Task",
        {
            "content": "comp",
            "project": project_a,
            "entity": shot_a,
            "step": pipeline_step_cmp,
            "task_assignees": [person_a],
        },
    )
    sg.create(
        "Task",
        {
            "content": "comp",
            "project": project_a,
            "entity": shot_b,
            "step": pipeline_step_cmp,
            "task_assignees": [person_a],
        },
    )
    task_lgt_a = sg.create(
        "Task",
        {
            "content": "lighting",
            "project": project_a,
            "entity": shot_a,
            "step": pipeline_step_lgt,
            "task_assignees": [person_a],
        },
    )
    task_mdl_a = sg.create(
        "Task",
        {
            "content": "modeling",
            "project": project_a,
            "entity": asset_tree_a,
            "step": pipeline_step_mdl,
            "task_assignees": [person_b],
        },
    )
    task_mdl_b = sg.create(
        "Task",
        {
            "content": "modeling",
            "project": project_a,
            "entity": asset_car_a,
            "step": pipeline_step_mdl,
            "task_assignees": [person_b],
        },
    )

    # PublishedFileTypes
    pub_type_alembic = sg.create("PublishedFileType", {"code": "Alembic Cache"})
    pub_type_render = sg.create("PublishedFileType", {"code": "Rendered Image"})

    # PublishedFiles
    for i in range(1, 6):
        sg.create(
            "PublishedFile",
            {
                "code": f"sh1111_city_v{i:03d}.%04d.exr",
                "name": "sh1111_city",
                "version_number": i,
                "published_file_type": pub_type_render,
                "project": project_a,
                "task": task_cmp_a,
                "entity": shot_a,
                "path": {
                    "content_type": "image/exr",
                    "link_type": "local",
                    "name": f"sh1111_city_v{i:03d}.%04d.exr",
                    "local_storage": local_storage,
                    "local_path_mac": f"/Volumes/projects/tp/sequences/sq111/"
                    f"sh1111_city_v{i:03d}.%04d.exr",
                    "local_path_linux": f"/mnt/projects/tp/sequences/sq111/"
                    f"sh1111_city_v{i:03d}.%04d.exr",
                    "local_path_windows": f"P:\\tp\\sequences\\sq111\\"
                    f"sh1111_city_v{i:03d}.%04d.exr",
                    "type": "Attachment",
                    "id": random.randint(1, 1000),
                    "local_path": f"/mnt/projects/tp/sequences/sq111/sh1111_city_v{i:03d}.%04d.exr",
                    "url": f"file:///mnt/projects/tp/sequences/sq111/sh1111_city_v{i:03d}.%04d.exr",
                },
                "path_cache": f"tp/sequences/sq111/sh1111_city_v{i:03d}.%04d.exr",
                "path_cache_storage": local_storage,
                "created_by": person_a,
            },
        )
    for i in range(1, 6):
        sg.create(
            "PublishedFile",
            {
                "code": f"sh1111_city_v{i:03d}.abc",
                "name": "sh1111_city",
                "version_number": i,
                "published_file_type": pub_type_alembic,
                "project": project_a,
                "task": task_lgt_a,
                "entity": shot_a,
                "path": {
                    "content_type": "image/exr",
                    "link_type": "local",
                    "name": f"sh1111_city_v{i:03d}.%04d.abc",
                    "local_storage": local_storage,
                    "local_path_mac": f"/Volumes/projects/tp/sequences/sq111/"
                    f"sh1111_city_v{i:03d}.%04d.abc",
                    "local_path_linux": f"/mnt/projects/tp/sequences/sq111/"
                    f"sh1111_city_v{i:03d}.%04d.abc",
                    "local_path_windows": f"P:\\tp\\sequences\\sq111\\"
                    f"sh1111_city_v{i:03d}.%04d.abc",
                    "type": "Attachment",
                    "id": random.randint(1, 1000),
                    "local_path": f"/mnt/projects/tp/sequences/sq111/sh1111_city_v{i:03d}.%04d.abc",
                    "url": f"file:///mnt/projects/tp/sequences/sq111/sh1111_city_v{i:03d}.%04d.abc",
                },
                "path_cache": f"tp/sequences/sq111/sh1111_city_v{i:03d}.abc",
                "path_cache_storage": local_storage,
                "created_by": person_b,
            },
        )

    sg.create(
        "PublishedFile",
        {
            "code": "CarA_mdl_v001.abc",
            "name": "CarA_mdl",
            "version_number": 1,
            "published_file_type": pub_type_alembic,
            "project": project_a,
            "task": task_mdl_b,
            "entity": asset_car_a,
            "path": None,
            "path_cache": "",
            "path_cache_storage": None,
            "created_by": person_b,
        },
    )
    sg.create(
        "PublishedFile",
        {
            "code": "CarA_mdl_v002.abc",
            "name": "CarA_mdl",
            "version_number": 2,
            "published_file_type": pub_type_alembic,
            "project": project_a,
            "task": task_mdl_b,
            "entity": asset_car_a,
            "path": {
                "content_type": None,
                "id": 123455,
                "link_type": "web",
                "name": "google",
                "type": "Attachment",
                "url": "https://www.google.com/",
            },
            "path_cache": "",
            "path_cache_storage": None,
            "created_by": person_b,
        },
    )
    sg.create(
        "PublishedFile",
        {
            "code": "CarA_mdl_v003.abc",
            "name": "CarA_mdl",
            "version_number": 3,
            "published_file_type": pub_type_alembic,
            "project": project_a,
            "task": task_mdl_b,
            "entity": asset_car_a,
            "path": {
                "content_type": None,
                "id": 123456,
                "link_type": "upload",
                "name": "test.txt",
                "type": "Attachment",
                "url": "https://sg-media-ireland.s3-accelerate.amazonaws.com/ffeb...",
            },
            "path_cache": "",
            "path_cache_storage": None,
            "created_by": person_b,
        },
    )

    # Playlists
    playlist_a = sg.create("Playlist", {"code": "Playlist A", "project": project_a})
    playlist_b = sg.create("Playlist", {"code": "Playlist B", "project": project_b})
    sg.create("Playlist", {"code": "Playlist C"})

    # PipelineConfigurations
    sg.create("PipelineConfiguration", {"code": "Primary"})
    sg.create("PipelineConfiguration", {"code": "Primary", "project": project_a})
    sg.create("PipelineConfiguration", {"code": "Develop", "project": project_a})

    # Versions
    sg_version_a = sg.create(
        "Version",
        {
            "code": "sh1111_city_v001",
            "user": person_a,
            "created_at": datetime.datetime(2000, 1, 1, 12, 0, 0),
            "sg_task": task_cmp_a,
            "entity": shot_a,
            "project": project_a,
            "playlists": [playlist_a],
        },
    )
    sg.create(
        "Version",
        {
            "code": "sh1111_city_v002",
            "user": person_a,
            "created_at": datetime.datetime(2000, 1, 2, 12, 0, 0),
            "sg_task": task_cmp_a,
            "entity": shot_a,
            "project": project_a,
            "playlists": [playlist_a],
        },
    )
    sg.create(
        "Version",
        {
            "code": "Tree_mdl_v001",
            "user": person_b,
            "created_at": datetime.datetime(2000, 1, 1, 12, 0, 0),
            "sg_task": task_mdl_a,
            "entity": asset_tree_a,
            "project": project_a,
            "playlists": [playlist_b],
        },
    )

    # Notes
    sg_note_a = sg.create("Note", {"subject": "Test note", "note_links": [sg_version_a]})

    # Replies
    sg.create("Reply", {"content": "Test reply", "entity": sg_note_a, "user": person_a})

    # Tags
    sg.create("Tag", {"name": "Vegetation"})
