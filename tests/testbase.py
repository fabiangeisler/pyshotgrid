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
        resources_dir = os.path.join(os.path.dirname(__file__), "resources")

        mockgun_schema_dir = os.path.join(
            resources_dir, "mockgun_schemas", "py{}".format(sys.version_info.major)
        )
        mockgun.Shotgun.set_schema_paths(
            os.path.join(mockgun_schema_dir, "schema.db"),
            os.path.join(mockgun_schema_dir, "entity_schema.db"),
        )
        cls.sg = mockgun.Shotgun(
            base_url="https://test.shotgunstudio.com",
            script_name="Unittest User",
            api_key="$ome_password",
        )

    @classmethod
    def add_default_entities(cls):
        # HumanUsers
        person_a = cls.sg.create(
            "HumanUser",
            {
                "firstname": "Alice",
                "lastname": "Alpha",
                "name": "Alice Alpha",
                "login": "alice.alpha",
                "email": "alice@company.com",
            },
        )
        person_b = cls.sg.create(
            "HumanUser",
            {
                "firstname": "Bob",
                "lastname": "Beta",
                "name": "Bob Beta",
                "login": "bob.beta",
                "email": "bob@company.com",
            },
        )
        person_c = cls.sg.create(
            "HumanUser",
            {
                "firstname": "Carol",
                "lastname": "Clown",
                "name": "Carol Clown",
                "login": "carol.clown",
                "email": "carol@company.com",
            },
        )

        # LocalStorages
        local_storage = cls.sg.create(
            "LocalStorage",
            {
                "code": "primary",
                "mac_path": "/Volumes/projects",
                "windows_path": "P:\\",
                "linux_path": "/mnt/projects",
            },
        )

        # Pipeline Steps
        pipeline_step_a = cls.sg.create(
            "Step",
            {
                "code": "Compositing",
                "short_name": "CMP",
            },
        )

        # Projects
        project_a = cls.sg.create(
            "Project",
            {
                "name": "Test Project A",
                "tank_name": "tpa",
                "users": [person_a, person_b, person_c],
            },
        )
        project_b = cls.sg.create(
            "Project",
            {
                "name": "Test Project B",
                "tank_name": "tpb",
                "users": [person_a, person_b, person_c],
            },
        )

        # Assets
        cls.sg.create("Asset", {"code": "Tree", "project": project_a})
        cls.sg.create("Asset", {"code": "CarA", "project": project_a})
        cls.sg.create("Asset", {"code": "CarB", "project": project_a})

        # Sequences
        sq111 = cls.sg.create("Sequence", {"code": "sq111", "project": project_a})
        sq222 = cls.sg.create("Sequence", {"code": "sq222", "project": project_a})

        # Shots
        shot_a = cls.sg.create(
            "Shot", {"code": "sq111_sh1111", "project": project_a, "sg_sequence": sq111}
        )
        cls.sg.create(
            "Shot", {"code": "sq111_sh2222", "project": project_a, "sg_sequence": sq111}
        )
        cls.sg.create(
            "Shot", {"code": "sq222_sh3333", "project": project_a, "sg_sequence": sq222}
        )
        cls.sg.create(
            "Shot", {"code": "sq222_sh4444", "project": project_a, "sg_sequence": sq222}
        )

        # Tasks
        cls.sg.create(
            "Task",
            {
                "content": "comp",
                "project": project_a,
                "entity": shot_a,
                "step": pipeline_step_a,
                "task_assignees": [person_a],
            },
        )

        # PublishedFiles
        cls.sg.create(
            "PublishedFile",
            {
                "code": "0010_v001.%04d.exr",
                "project": project_a,
                "path_cache": "tp/sequences/0010_v001.%04d.exr",
                "path_cache_storage": local_storage,
            },
        )

        # Playlists
        cls.sg.create("Playlist", {"code": "Playlist A", "project": project_a})
        cls.sg.create("Playlist", {"code": "Playlist B", "project": project_b})
        cls.sg.create("Playlist", {"code": "Playlist C"})

        # PipelineConfigurations
        cls.sg.create("PipelineConfiguration", {"code": "Primary"})
        cls.sg.create(
            "PipelineConfiguration", {"code": "Primary", "project": project_a}
        )
        cls.sg.create(
            "PipelineConfiguration", {"code": "Develop", "project": project_a}
        )

        # Notes
        cls.sg.create("Note", {"subject": "Test note"})
