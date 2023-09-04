"""Tests for `pyshotgrid` core.Field class."""
import pyshotgrid as pysg


def test_name(sg):
    sg_project = pysg.new_entity(sg, 1, "Project")
    sg_name_field = pysg.core.Field("name", sg_project)

    result = sg_name_field.name

    assert "name" == result


def test_entity(sg):
    sg_project = pysg.new_entity(sg, 1, "Project")
    sg_name_field = pysg.core.Field("name", sg_project)

    result = sg_name_field.entity

    assert sg_project == result


def test_string_representation(sg):
    sg_project = pysg.new_entity(sg, 1, "Project")
    sg_name_field = pysg.core.Field("name", sg_project)

    result = str(sg_name_field)

    assert "Field - name - Entity: Project ID: 1" == result


def test_get(sg):
    sg_project = pysg.new_entity(sg, 1, "Project")
    sg_name_field = pysg.core.Field("name", sg_project)

    result = sg_name_field.get()

    assert "Test Project A" == result


def test_get__url_field_no_value(sg):
    sg_publish = pysg.new_site(sg).find_one("PublishedFile", [["code", "is", "CarA_mdl_v001.abc"]])
    sg_path_field = pysg.core.Field("path", sg_publish)

    result = sg_path_field.get()

    assert result is None


def test_get__url_field_web_url(sg):
    sg_publish = pysg.new_site(sg).find_one("PublishedFile", [["code", "is", "CarA_mdl_v002.abc"]])
    sg_path_field = pysg.core.Field("path", sg_publish)

    result = sg_path_field.get()

    assert result == "https://www.google.com/"


def test_get__url_field_upload_value(sg):
    sg_publish = pysg.new_site(sg).find_one("PublishedFile", [["code", "is", "CarA_mdl_v003.abc"]])
    sg_path_field = pysg.core.Field("path", sg_publish)

    result = sg_path_field.get()

    assert result == {
        "content_type": None,
        "id": 123456,
        "link_type": "upload",
        "name": "test.txt",
        "type": "Attachment",
        "url": "https://sg-media-ireland.s3-accelerate.amazonaws.com/ffeb...",
    }


def test_get__url_field_local_path_value(sg):
    sg_publish = pysg.new_site(sg).find_one(
        "PublishedFile", [["code", "is", "sh1111_city_v001.%04d.exr"]]
    )
    sg_path_field = pysg.core.Field("path", sg_publish)

    result = sg_path_field.get()

    assert result == "/mnt/projects/tp/sequences/sq111/sh1111_city_v001.%04d.exr"


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


def test_add(sg):
    sg_project = pysg.new_entity(sg, 1, "Project")
    sg_person = pysg.new_entity(sg, 4, "HumanUser")
    sg_users_field = pysg.core.Field("users", sg_project)
    assert sg_person not in sg_users_field.get()

    sg_users_field.add([sg_person])

    assert sg_person in sg_users_field.get()
    # Cleanup
    sg_users_field.remove([sg_person])


def test_remove(sg):
    sg_project = pysg.new_entity(sg, 1, "Project")
    sg_person = pysg.new_entity(sg, 1, "HumanUser")
    sg_users_field = pysg.core.Field("users", sg_project)
    assert sg_person in sg_users_field.get()

    sg_users_field.remove([sg_person])

    assert sg_person not in sg_users_field.get()
    # Cleanup
    sg_users_field.add([sg_person])


def test_schema(sg):
    sg_project = pysg.new_entity(sg, 1, "Project")
    sg_name_field = pysg.core.Field("name", sg_project)

    result = sg_name_field.schema

    assert isinstance(result, pysg.FieldSchema)
    assert result.name == "name"
    assert result.entity_type == "Project"


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
