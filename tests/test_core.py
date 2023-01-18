"""Tests for `pyshotgrid.core` module."""

import pyshotgrid as pysg

from .testbase import BaseShotGridTest


class TestCoreConvertFunctions(BaseShotGridTest):
    @classmethod
    def setUpClass(cls):
        super(TestCoreConvertFunctions, cls).setUpClass()

        cls.add_default_entities()

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
    @classmethod
    def setUpClass(cls):
        super(TestCoreNewFunctions, cls).setUpClass()

        cls.add_default_entities()

    def test_new_entity(self):
        sg_entity_a = pysg.new_entity(self.sg, {"type": "Project", "id": 1})
        sg_entity_b = pysg.new_entity(self.sg, "Project", 1)
        sg_entity_c = pysg.new_entity(self.sg, entity_type="Project", entity_id=1)

        self.assertTrue(sg_entity_a == sg_entity_b == sg_entity_c)
