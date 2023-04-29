"""Tests for `pyshotgrid` SGSite class."""
from shotgun_api3.lib import mockgun

import pyshotgrid as pysg
import pyshotgrid.sg_default_entities as sde

from .testbase import BaseShotGridTest


class TestSGSite(BaseShotGridTest):
    """Tests for `pyshotgrid` package."""

    def test_people(self):
        sg_site = pysg.SGSite(self.sg)

        result = sg_site.people()

        self.assertEqual(3, len(result))
        self.assertTrue(isinstance(result[0], sde.SGHumanUser))

    def test_pipeline_configuration(self):
        sg_site = pysg.SGSite(self.sg)

        result = sg_site.pipeline_configuration()

        self.assertTrue(isinstance(result, sde.SGEntity))

    def test_pipeline_configuration__by_name(self):
        sg_site = pysg.SGSite(self.sg)

        result = sg_site.pipeline_configuration(name_or_id="Primary")

        self.assertTrue(isinstance(result, sde.SGEntity))
        self.assertEqual("Primary", result["code"].get())

    def test_pipeline_configuration__by_id(self):
        sg_site = pysg.SGSite(self.sg)

        result = sg_site.pipeline_configuration(name_or_id=1)

        self.assertTrue(isinstance(result, sde.SGEntity))
        self.assertEqual(1, result.id)

    def test_pipeline_configuration__by_project(self):
        sg_project = pysg.new_entity(self.sg, "Project", 1)
        sg_site = pysg.SGSite(self.sg)

        result = sg_site.pipeline_configuration(project=sg_project)

        self.assertTrue(isinstance(result, sde.SGEntity))
        self.assertEqual(sg_project, result["project"].get())

    def test_entity_field_schemas(self):
        sg_site = pysg.SGSite(self.sg)

        result = sg_site.entity_field_schemas()

        self.assertTrue(isinstance(result["Project"]["code"], pysg.FieldSchema))

    def test_comparison(self):
        sg_site_a = pysg.SGSite(self.sg)
        sg_site_b = pysg.SGSite(self.sg)

        result = sg_site_a == sg_site_b

        self.assertTrue(result)

    def test_comparison__inequality(self):
        sg_site_a = pysg.SGSite(self.sg)
        other_sg = mockgun.Shotgun(
            base_url="https://other.shotgunstudio.com",
            script_name="Unittest User",
            api_key="$ome_password",
        )
        sg_site_b = pysg.SGSite(other_sg)

        result = sg_site_a != sg_site_b

        self.assertTrue(result)

    def test_comparison__wrong_type(self):
        sg_site_a = pysg.SGSite(self.sg)

        result = sg_site_a != 1

        self.assertTrue(result)
