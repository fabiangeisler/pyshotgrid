"""Tests for `pyshotgrid` SGSite class."""
import pyshotgrid as pysg
import pyshotgrid.field
import pyshotgrid.sg_default_entities as sde

from .testbase import BaseShotGridTest


class TestSGSite(BaseShotGridTest):
    """Tests for `pyshotgrid` package."""

    @classmethod
    def setUpClass(cls):
        super(TestSGSite, cls).setUpClass()

        cls.add_default_entities()

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

        self.assertTrue(
            isinstance(result["Project"]["code"], pyshotgrid.field.FieldSchema)
        )
