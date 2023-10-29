"""Tests for `pyshotgrid.core` module."""
import unittest.mock

import pytest

import pyshotgrid as pysg


def test_convert_filters_to_dict(sg):
    person = pysg.SGEntity(sg, entity_type="HumanUser", entity_id=2)

    result = pysg.core.convert_filters_to_dict([["user", "is", person]])

    assert [["user", "is", {"type": "HumanUser", "id": 2}]] == result


def test_convert_filters_to_dict__list_of_entities(sg):
    person_a = pysg.SGEntity(sg, entity_type="HumanUser", entity_id=1)
    person_b = pysg.SGEntity(sg, entity_type="HumanUser", entity_id=2)

    result = pysg.core.convert_filters_to_dict([["user", "in", [person_a, person_b]]])

    assert [
        [
            "user",
            "in",
            [{"type": "HumanUser", "id": 1}, {"type": "HumanUser", "id": 2}],
        ]
    ] == result


def test_convert_filters_to_dict__list_of_non_entity_values(sg):
    result = pysg.core.convert_filters_to_dict([["priority", "in", [10, 20, 30]]])

    assert [["priority", "in", [10, 20, 30]]] == result


def test_convert_value_to_pysg__no_entity_value(sg):
    example_value = "some other value than an entity"

    result = pysg.core.convert_value_to_pysg(sg, example_value)

    assert example_value == result


def test_convert_value_to_pysg__single_entity(sg):
    person_a = pysg.SGEntity(sg, entity_type="HumanUser", entity_id=1)

    result = pysg.core.convert_value_to_pysg(sg, {"type": "HumanUser", "id": 1})

    assert person_a == result


def test_convert_value_to_pysg__list_of_entities(sg):
    person_a = pysg.SGEntity(sg, entity_type="HumanUser", entity_id=1)
    person_b = pysg.SGEntity(sg, entity_type="HumanUser", entity_id=2)

    result = pysg.core.convert_value_to_pysg(
        sg, [{"type": "HumanUser", "id": 1}, {"type": "HumanUser", "id": 2}]
    )

    assert [person_a, person_b] == result


def test_convert_value_to_dict__no_entity_value(sg):
    example_value = "some other value than an entity"

    result = pysg.core.convert_value_to_dict(example_value)

    assert example_value == result


def test_convert_value_to_dict__single_entity(sg):
    person_a = pysg.SGEntity(sg, entity_type="HumanUser", entity_id=1)

    result = pysg.core.convert_value_to_dict(person_a)

    assert {"type": "HumanUser", "id": 1} == result


def test_convert_value_to_dict__list_of_entities(sg):
    person_a = pysg.SGEntity(sg, entity_type="HumanUser", entity_id=1)
    person_b = {"type": "HumanUser", "id": 2}

    result = pysg.core.convert_value_to_dict([person_a, person_b])

    assert [{"type": "HumanUser", "id": 1}, {"type": "HumanUser", "id": 2}] == result


def test_new_entity(sg):
    sg_entity_a = pysg.new_entity(sg, {"type": "Project", "id": 1})
    sg_entity_b = pysg.new_entity(sg, 1, "Project")
    sg_entity_c = pysg.new_entity(sg, entity_type="Project", entity_id=1)

    assert sg_entity_a == sg_entity_b == sg_entity_c


def test_new_entity__raises_error_on_wrong_inputs(sg):
    with pytest.raises(ValueError):
        pysg.new_entity(sg, 123)


def test_new_site(sg):
    sg_site_a = pysg.new_site(sg)

    assert isinstance(sg_site_a, pysg.SGSite)


def test_new_site__args(sg):
    with unittest.mock.patch("shotgun_api3.Shotgun"):
        sg_site_a = pysg.new_site(
            "https://test.shotgunstudio.com",
            "Unittest User",
            "$ome_password",
        )

    assert isinstance(sg_site_a, pysg.SGSite)


def test_new_site__kwargs(sg):
    with unittest.mock.patch("shotgun_api3.Shotgun"):
        sg_site_a = pysg.new_site(
            base_url="https://test.shotgunstudio.com",
            script_name="Unittest User",
            api_key="$ome_password",
        )

    assert isinstance(sg_site_a, pysg.SGSite)


class SGNote(pysg.SGEntity):
    """
    Test SGEntity class.
    """

    DEFAULT_SG_ENTITY_TYPE = "Note"


class CustomSGProject(pysg.sg_default_entities.SGProject):
    """
    Test class from default SGEntity.
    """

    DEFAULT_SG_ENTITY_TYPE = "Project"


class CustomSGSite(pysg.SGSite):
    """
    Test SGSite class.
    """


def test_register_pysg_class__add_custom_sg_class(sg):
    pysg.register_pysg_class(SGNote)
    sg_entity_a = pysg.new_entity(sg, {"type": "Note", "id": 1})

    result = sg_entity_a.__class__

    assert SGNote == result


def test_register_pysg_class__overwrite_default_sg_class(sg):
    pysg.register_pysg_class(CustomSGProject)
    sg_entity_a = pysg.new_entity(sg, {"type": "Project", "id": 1})

    result = sg_entity_a.__class__

    assert CustomSGProject == result


def test_register_pysg_class__errors_on_invalid_class(sg):
    with pytest.raises(TypeError):
        pysg.register_pysg_class(str, "Project")  # type: ignore


def test_register_pysg_class__errors_when_no_entity_type_can_be_detected(sg):
    class ClassWithMissingDEFAULTSGENTITYTYPE(pysg.SGEntity):
        """
        Class with missing DEFAULT_SG_ENTITY_TYPE
        """

    with pytest.raises(ValueError):
        pysg.register_pysg_class(ClassWithMissingDEFAULTSGENTITYTYPE)


def test_register_sg_site_class__add_custom_class(sg):
    pysg.register_sg_site_class(CustomSGSite)
    sg_entity_a = pysg.new_site(sg)

    result = sg_entity_a.__class__

    assert CustomSGSite == result


def test_register_sg_site_class__errors_on_invalid_class(sg):
    with pytest.raises(TypeError):
        pysg.register_sg_site_class(str)  # type: ignore
