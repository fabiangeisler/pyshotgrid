"""Tests for `pyshotgrid` default entities."""
import pyshotgrid.sg_default_entities as sde

from .testbase import BaseShotGridTest


class TestSGProject(BaseShotGridTest):
    """Tests for `pyshotgrid` package."""

    @classmethod
    def setUpClass(cls):
        super(TestSGProject, cls).setUpClass()

        cls.add_default_entities()

    def test_shots(self):
        sg_project = sde.SGProject(self.sg, 1)

        result = sg_project.shots()

        self.assertEqual(4, len(result))
        self.assertTrue(isinstance(result[0], sde.SGShot))

    def test_shots_glob(self):
        sg_project = sde.SGProject(self.sg, 1)

        result = sg_project.shots("sq111_*")

        self.assertEqual(2, len(result))
        self.assertEqual("sq111_sh1111", result[0]["code"].get())
        self.assertEqual("sq111_sh2222", result[1]["code"].get())

    def test_assets(self):
        sg_project = sde.SGProject(self.sg, 1)

        result = sg_project.assets()

        self.assertEqual(3, len(result))
        self.assertTrue(isinstance(result[0], sde.SGAsset))

    def test_assets_glob(self):
        sg_project = sde.SGProject(self.sg, 1)

        result = sg_project.assets("Car*")

        self.assertEqual(2, len(result))
        self.assertEqual("CarA", result[0]["code"].get())
        self.assertEqual("CarB", result[1]["code"].get())

    def test_playlists(self):
        sg_project = sde.SGProject(self.sg, 1)

        result = sg_project.playlists()

        self.assertEqual(1, len(result))
        self.assertTrue(isinstance(result[0], sde.SGPlaylist))
