"""Tests for `pyshotgrid` core.Field class."""
import pytest

import pyshotgrid as pysg


def test_name(sg):
    sg_project = pysg.new_entity(sg, 1, "Project")
    sg_name_field = pysg.core.Field("name", sg_project)

    result = sg_name_field.name

    assert "name" == result


def test_display_name(sg):
    sg_project = pysg.new_entity(sg, 1, "Project")
    sg_name_field = pysg.core.Field("name", sg_project)

    result = sg_name_field.display_name

    assert "Project Name" == result


def test_description(sg):
    sg_project = pysg.new_entity(sg, 1, "Project")
    sg_name_field = pysg.core.Field("name", sg_project)

    result = sg_name_field.description

    assert "" == result


def test_data_type(sg):
    sg_project = pysg.new_entity(sg, 1, "Project")
    sg_name_field = pysg.core.Field("name", sg_project)

    result = sg_name_field.data_type

    assert "text" == result


@pytest.mark.skip(
    'mockgun.schema_field_update() is missing argument "project_entity".'
    "This text cannot work."
)
def test_description__set(sg):
    sg_project = pysg.new_entity(sg, 1, "Project")
    sg_name_field = pysg.core.Field("name", sg_project)

    sg_name_field.description = "The name of the Project."

    assert "The name of the Project." == sg_name_field.description


def test_entity(sg):
    sg_project = pysg.new_entity(sg, 1, "Project")
    sg_name_field = pysg.core.Field("name", sg_project)

    result = sg_name_field.entity

    assert sg_project == result


def test_string_representation(sg):
    sg_project = pysg.new_entity(sg, 1, "Project")
    sg_name_field = pysg.core.Field("name", sg_project)

    result = str(sg_name_field)

    assert "Field - name - Entity: Project Entity ID: 1" == result


def test_get(sg):
    sg_project = pysg.new_entity(sg, 1, "Project")
    sg_name_field = pysg.core.Field("name", sg_project)

    result = sg_name_field.get()

    assert "Test Project A" == result


def test_get_raw_values(sg):
    sg_project = pysg.new_entity(sg, 1, "Project")
    sg_users_field = pysg.core.Field("users", sg_project)

    result = sg_users_field.get(raw_values=True)

    assert [
        {"id": 1, "type": "HumanUser"},
        {"id": 2, "type": "HumanUser"},
        {"id": 3, "type": "HumanUser"},
    ] == result


def test_set(sg):
    sg_project = pysg.new_entity(sg, 1, "Project")
    sg_name_field = pysg.core.Field("name", sg_project)

    sg_name_field.set("FooBar")

    assert "FooBar" == sg_name_field.get()


def test_batch_update_dict(sg):
    sg_project = pysg.new_entity(sg, 1, "Project")
    sg_name_field = pysg.core.Field("name", sg_project)

    result = sg_name_field.batch_update_dict("FooBar")

    assert {
        "request_type": "update",
        "entity_type": "Project",
        "entity_id": 1,
        "data": {"name": "FooBar"},
    } == result


@pytest.mark.skip(
    'Mockgun.update is missing the "multi_entity_update_modes" parameter. '
    "This test cannot work."
)
def test_remove(sg):
    sg_project = pysg.new_entity(sg, 1, "Project")
    sg_human_user = pysg.new_entity(sg, 1, "HumanUser")
    sg_users_field = pysg.core.Field("users", sg_project)

    sg_users_field.remove([sg_human_user])
    sg_users_field.remove([{"id": 2, "type": "HumanUser"}])

    assert [{"id": 3, "type": "HumanUser"}] == sg_users_field.get()
