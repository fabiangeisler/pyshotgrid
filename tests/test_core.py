"""Tests for `pyshotgrid.core` module."""

import pyshotgrid as pysg

from .testbase import BaseShotGridTest


class TestCoreConvertFunctions(BaseShotGridTest):
    def test_convert_filters_to_dict(self):
        person = pysg.SGEntity(self.sg, entity_type="HumanUser", entity_id=2)

        result = pysg.core.convert_filters_to_dict([["user", "is", person]])

        self.assertEqual([["user", "is", {"type": "HumanUser", "id": 2}]], result)

    def test_convert_filters_to_dict__list_of_entities(self):
        person_a = pysg.SGEntity(self.sg, entity_type="HumanUser", entity_id=1)
        person_b = pysg.SGEntity(self.sg, entity_type="HumanUser", entity_id=2)

        result = pysg.core.convert_filters_to_dict(
            [["user", "in", [person_a, person_b]]]
        )

        self.assertEqual(
            [
                [
                    "user",
                    "in",
                    [{"type": "HumanUser", "id": 1}, {"type": "HumanUser", "id": 2}],
                ]
            ],
            result,
        )

    def test_convert_filters_to_dict__list_of_non_entity_values(self):
        result = pysg.core.convert_filters_to_dict([["priority", "in", [10, 20, 30]]])

        self.assertEqual([["priority", "in", [10, 20, 30]]], result)

    def test_convert_value_to_pysg__no_entity_value(self):
        example_value = "some other value than an entity"

        result = pysg.core.convert_value_to_pysg(self.sg, example_value)

        self.assertEqual(example_value, result)

    def test_convert_value_to_pysg__single_entity(self):
        person_a = pysg.SGEntity(self.sg, entity_type="HumanUser", entity_id=1)

        result = pysg.core.convert_value_to_pysg(
            self.sg, {"type": "HumanUser", "id": 1}
        )

        self.assertEqual(person_a, result)

    def test_convert_value_to_pysg__list_of_entities(self):
        person_a = pysg.SGEntity(self.sg, entity_type="HumanUser", entity_id=1)
        person_b = pysg.SGEntity(self.sg, entity_type="HumanUser", entity_id=2)

        result = pysg.core.convert_value_to_pysg(
            self.sg, [{"type": "HumanUser", "id": 1}, {"type": "HumanUser", "id": 2}]
        )

        self.assertEqual([person_a, person_b], result)

    def test_convert_value_to_dict__no_entity_value(self):
        example_value = "some other value than an entity"

        result = pysg.core.convert_value_to_dict(example_value)

        self.assertEqual(example_value, result)

    def test_convert_value_to_dict__single_entity(self):
        person_a = pysg.SGEntity(self.sg, entity_type="HumanUser", entity_id=1)

        result = pysg.core.convert_value_to_dict(person_a)

        self.assertEqual({"type": "HumanUser", "id": 1}, result)

    def test_convert_value_to_dict__list_of_entities(self):
        person_a = pysg.SGEntity(self.sg, entity_type="HumanUser", entity_id=1)
        person_b = pysg.SGEntity(self.sg, entity_type="HumanUser", entity_id=2)

        result = pysg.core.convert_value_to_dict([person_a, person_b])

        self.assertEqual(
            [{"type": "HumanUser", "id": 1}, {"type": "HumanUser", "id": 2}], result
        )


class TestCoreNewFunctions(BaseShotGridTest):
    def setUp(self):
        pysg.core.__ENTITY_PLUGINS = {}

    def test_new_entity(self):
        sg_entity_a = pysg.new_entity(self.sg, {"type": "Project", "id": 1})
        sg_entity_b = pysg.new_entity(self.sg, "Project", 1)
        sg_entity_c = pysg.new_entity(self.sg, entity_type="Project", entity_id=1)

        self.assertTrue(sg_entity_a == sg_entity_b == sg_entity_c)

    def test_new_entity__raises_error_on_wrong_inputs(self):
        with self.assertRaises(ValueError):
            pysg.new_entity(self.sg, 123)

    def test_new_site(self):
        sg_site_a = pysg.new_site(self.sg)

        self.assertTrue(isinstance(sg_site_a, pysg.SGSite))


class SGNote(pysg.SGEntity):
    """
    Test SGEntity class.
    """


class CustomSGProject(pysg.sg_default_entities.SGProject):
    """
    Test class from default SGEntity.
    """


class CustomSGSite(pysg.SGSite):
    """
    Test SGSite class.
    """


class TestCorePluginFunctions(BaseShotGridTest):
    def test_register_pysg_class__add_custom_sg_class(self):
        pysg.register_pysg_class("Note", SGNote)
        sg_entity_a = pysg.new_entity(self.sg, {"type": "Note", "id": 1})

        result = sg_entity_a.__class__

        self.assertTrue(SGNote == result)

    def test_register_pysg_class__overwrite_default_sg_class(self):
        pysg.register_pysg_class("Project", CustomSGProject)
        sg_entity_a = pysg.new_entity(self.sg, {"type": "Project", "id": 1})

        result = sg_entity_a.__class__

        self.assertTrue(CustomSGProject == result)

    def test_register_pysg_class__errors_on_invalid_class(self):
        with self.assertRaises(TypeError):
            pysg.register_pysg_class("Project", str)  # type: ignore

    def test_register_sg_site_class__add_custom_class(self):
        pysg.register_sg_site_class(CustomSGSite)
        sg_entity_a = pysg.new_site(self.sg)

        result = sg_entity_a.__class__

        self.assertTrue(CustomSGSite == result)

    def test_register_sg_site_class__errors_on_invalid_class(self):
        with self.assertRaises(TypeError):
            pysg.register_sg_site_class(str)  # type: ignore
