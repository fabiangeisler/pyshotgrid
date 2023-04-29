"""Tests for `pyshotgrid` default entities."""
import pyshotgrid.sg_default_entities as sde

from .testbase import BaseShotGridTest


class TestSGProject(BaseShotGridTest):
    """Tests for `SGProject` class."""

    def test_shots(self):
        sg_project = sde.SGProject(self.sg, "Project", 1)

        result = sg_project.shots()

        self.assertEqual(4, len(result))
        self.assertTrue(isinstance(result[0], sde.SGShot))

    def test_shots_glob(self):
        sg_project = sde.SGProject(self.sg, "Project", 1)

        result = sg_project.shots("sq111_*")

        self.assertEqual(2, len(result))
        self.assertEqual("sq111_sh1111", result[0]["code"].get())
        self.assertEqual("sq111_sh2222", result[1]["code"].get())

    def test_assets(self):
        sg_project = sde.SGProject(self.sg, "Project", 1)

        result = sg_project.assets()

        self.assertEqual(3, len(result))
        self.assertTrue(isinstance(result[0], sde.SGAsset))

    def test_assets_glob(self):
        sg_project = sde.SGProject(self.sg, "Project", 1)

        result = sg_project.assets("Car*")

        self.assertEqual(2, len(result))
        self.assertEqual("CarA", result[0]["code"].get())
        self.assertEqual("CarB", result[1]["code"].get())

    def test_playlists(self):
        sg_project = sde.SGProject(self.sg, "Project", 1)

        result = sg_project.playlists()

        self.assertEqual(1, len(result))
        self.assertTrue(isinstance(result[0], sde.SGPlaylist))


class TestSGPublishedFile(BaseShotGridTest):
    """Tests for `SGPublishedFile` class."""

    def test_is_latest__false(self):
        sg_publish = sde.SGPublishedFile(self.sg, "PublishedFile", 1)

        result = sg_publish.is_latest()

        self.assertFalse(result)

    def test_is_latest__true(self):
        sg_publish = sde.SGPublishedFile(self.sg, "PublishedFile", 5)

        result = sg_publish.is_latest()

        self.assertTrue(result)

    def test_get_latest_publish__is_already_latest(self):
        sg_publish = sde.SGPublishedFile(self.sg, "PublishedFile", 5)

        result = sg_publish.get_latest_publish()

        self.assertEqual(sg_publish, result)

    def test_get_latest_publish(self):
        sg_publish = sde.SGPublishedFile(self.sg, "PublishedFile", 1)
        latest_sg_publish = sde.SGPublishedFile(self.sg, "PublishedFile", 5)

        result = sg_publish.get_latest_publish()

        self.assertEqual(latest_sg_publish, result)

    def test_get_all_publishes(self):
        sg_publishes = [
            sde.SGPublishedFile(self.sg, "PublishedFile", i) for i in range(1, 6)
        ]

        result = sg_publishes[0].get_all_publishes()

        self.assertEqual(sg_publishes, result)

    def test_get_next_publishes(self):
        sg_publish = sde.SGPublishedFile(self.sg, "PublishedFile", 3)
        result_sg_publishes = [
            sde.SGPublishedFile(self.sg, "PublishedFile", i) for i in range(4, 6)
        ]

        result = sg_publish.get_next_publishes()

        self.assertEqual(result_sg_publishes, result)

    def test_get_previous_publishes(self):
        sg_publish = sde.SGPublishedFile(self.sg, "PublishedFile", 3)
        result_sg_publishes = [
            sde.SGPublishedFile(self.sg, "PublishedFile", i) for i in range(1, 3)
        ]

        result = sg_publish.get_previous_publishes()

        self.assertEqual(result_sg_publishes, result)
