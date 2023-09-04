"""Tests for `pyshotgrid` package."""

from unittest import mock

import pytest
from shotgun_api3.lib import mockgun

import pyshotgrid
import pyshotgrid as pysg


def test_valueerror_when_project_type_is_missing(sg):
    with pytest.raises(ValueError):
        _ = pysg.SGEntity(sg, 1)


def test_string_representation(sg):
    sg_entity = pysg.SGEntity(sg, 1, "Project")

    assert (
        "SGEntity - Type: Project - ID: 1 - "
        "URL: https://test.shotgunstudio.com/detail/Project/1" == str(sg_entity)
    )


def test_query_field_dict_notation(sg):
    sg_entity = pysg.SGEntity(sg, 1, "Project")

    assert "tpa" == sg_entity["tank_name"].get()


def test_get(sg):
    sg_entity = pysg.SGEntity(sg, 1, "Project")

    assert {"name": "Test Project A", "tank_name": "tpa"} == sg_entity.get(["name", "tank_name"])


def test_get__url_field_no_value(sg):
    sg_publish = pysg.new_site(sg).find_one("PublishedFile", [["code", "is", "CarA_mdl_v001.abc"]])

    result = sg_publish.get(["code", "path"])

    assert result == {"code": "CarA_mdl_v001.abc", "path": None}


def test_get__url_field_web_url(sg):
    sg_publish = pysg.new_site(sg).find_one("PublishedFile", [["code", "is", "CarA_mdl_v002.abc"]])

    result = sg_publish.get(["code", "path"])

    assert result == {"code": "CarA_mdl_v002.abc", "path": "https://www.google.com/"}


def test_get__url_field_upload_value(sg):
    sg_publish = pysg.new_site(sg).find_one("PublishedFile", [["code", "is", "CarA_mdl_v003.abc"]])

    result = sg_publish.get(["code", "path"])

    assert result == {
        "code": "CarA_mdl_v003.abc",
        "path": {
            "content_type": None,
            "id": 123456,
            "link_type": "upload",
            "name": "test.txt",
            "type": "Attachment",
            "url": "https://sg-media-ireland.s3-accelerate.amazonaws.com/ffeb...",
        },
    }


def test_get__url_field_local_path_value(sg):
    sg_publish = pysg.new_site(sg).find_one(
        "PublishedFile", [["code", "is", "sh1111_city_v001.%04d.exr"]]
    )

    result = sg_publish.get(["code", "path"])

    assert result == {
        "code": "sh1111_city_v001.%04d.exr",
        "path": "/mnt/projects/tp/sequences/sq111/sh1111_city_v001.%04d.exr",
    }


def test_name(sg):
    sg_project = pysg.new_entity(sg, 1, "Project")
    sg_task = pysg.new_entity(sg, 1, "Task")
    sg_asset = pysg.new_entity(sg, 1, "Asset")
    sg_tag = pysg.new_entity(sg, 1, "Tag")

    result_project_name_field = sg_project.name
    result_task_name_field = sg_task.name
    result_asset_name_field = sg_asset.name
    result_tag_name_field = sg_tag.name

    assert "name" == result_project_name_field.name
    assert "content" == result_task_name_field.name
    assert "code" == result_asset_name_field.name
    assert "name" == result_tag_name_field.name


def test_thumbnail(sg):
    sg_task = pysg.new_entity(sg, 1, "Task")

    result_task_thumbnail_field = sg_task.thumbnail

    assert "image" == result_task_thumbnail_field.name


def test_filmstrip(sg):
    sg_task = pysg.new_entity(sg, 1, "Task")

    result_task_filmstrip_field = sg_task.filmstrip

    assert "filmstrip_image" == result_task_filmstrip_field.name


def test_name__errors_when_no_name_field_present(sg):
    sg_entity = pysg.new_entity(sg, 1, "Note")

    with pytest.raises(RuntimeError):
        _ = sg_entity.name


def test_set(sg):
    sg_entity = pysg.SGEntity(sg, 1, "Project")

    sg_entity.set({"code": "Test Name", "tank_name": "tn"})

    assert {"code": "Test Name", "tank_name": "tn"} == sg_entity.get(["code", "tank_name"])
    # Cleanup
    sg_entity.set({"code": "Test Project", "tank_name": "tp"})


def test_update_field_dict_notation(sg):
    sg_entity = pysg.SGEntity(sg, 1, "Project")
    sg_entity["code"].set("bar-baz")

    assert "bar-baz" == sg_entity["code"].get()

    # cleanup
    sg_entity["code"].set("Test project")


def test_convert_to_dict(sg):
    # published files to query publish form paths.
    sg_publish = sg.create("PublishedFile", {"code": "delete_me"})
    sg_entity = pysg.SGEntity(sg, sg_publish["id"], sg_publish["type"])

    sg_entity.delete()

    assert [] == sg.find(sg_publish["type"], [["id", "is", sg_publish["id"]]])


def test_delete(sg):
    sg_entity = pysg.SGEntity(sg, 1, "LocalStorage")

    assert {"id": 1, "type": "LocalStorage"} == sg_entity.to_dict()


def test_site(sg):
    sg_entity = pysg.SGEntity(sg, 1, "LocalStorage")

    assert isinstance(sg_entity.site, pysg.SGSite)


def test_iter_all_field_values(sg):
    sg_entity = pysg.SGEntity(sg, 1, "LocalStorage")

    # Mock Mockgun.schema_field_read - the "project_entity" arg is missing in Mockgun.
    with mock.patch.object(
        mockgun.Shotgun,
        "schema_field_read",
        return_value={
            "linux_path": {"visible": {"value": True}},
            "type": {"visible": {"value": True}},
            "id": {"visible": {"value": True}},
            "description": {"visible": {"value": True}},
            "cached_display_name": {"visible": {"value": True}},
            "mac_path": {"visible": {"value": True}},
            "created_at": {"visible": {"value": True}},
            "created_by": {"visible": {"value": True}},
            "windows_path": {"visible": {"value": True}},
            "uuid": {"visible": {"value": True}},
            "code": {"visible": {"value": True}},
            "updated_at": {"visible": {"value": True}},
            "updated_by": {"visible": {"value": True}},
        },
    ):
        result = set(sg_entity.all_field_values().items())

    assert {
        ("linux_path", "/mnt/projects"),
        ("type", "LocalStorage"),
        ("id", 1),
        ("description", None),
        ("cached_display_name", None),
        ("mac_path", "/Volumes/projects"),
        ("created_by", None),
        ("updated_by", None),
        ("created_at", None),
        ("windows_path", "P:\\"),
        ("uuid", None),
        ("code", "primary"),
        ("updated_at", None),
    } == result


def test_iter_all_field_values__raw(sg):
    sg_entity = pysg.SGEntity(sg, 1, "Reply")

    # Mock Mockgun.schema_field_read - the "project_entity" arg is missing in Mockgun.
    with mock.patch.object(
        mockgun.Shotgun,
        "schema_field_read",
        return_value={
            "content": {"visible": {"value": True, "editable": False}},
            "entity": {"visible": {"value": True, "editable": False}},
            "user": {"visible": {"value": True, "editable": False}},
            "publish_status": {"visible": {"value": True, "editable": False}},
            "cached_display_name": {"visible": {"value": True, "editable": False}},
            "created_at": {"visible": {"value": True, "editable": False}},
            "id": {"visible": {"value": True, "editable": False}},
        },
    ):
        result = sg_entity.all_field_values(raw_values=True)

    assert {
        "cached_display_name": None,
        "content": "Test reply",
        "created_at": None,
        "entity": {"id": 1, "type": "Note"},
        "id": 1,
        "publish_status": None,
        "type": "Reply",
        "user": {"id": 1, "type": "HumanUser"},
    } == result


def test_iter_all_field_values__project(sg):
    sg_entity = pysg.SGEntity(sg, 1, "LocalStorage")
    sg_project = pysg.SGEntity(sg, 1, "Project")

    # Mock Mockgun.schema_field_read - the "project_entity" arg is missing in Mockgun.
    with mock.patch.object(
        mockgun.Shotgun,
        "schema_field_read",
        return_value={
            "linux_path": {"visible": {"value": True}},
            "type": {"visible": {"value": True}},
            "id": {"visible": {"value": True}},
            "description": {"visible": {"value": True}},
            "cached_display_name": {"visible": {"value": True}},
            "mac_path": {"visible": {"value": True}},
            "created_at": {"visible": {"value": True}},
            "created_by": {"visible": {"value": True}},
            "windows_path": {"visible": {"value": True}},
            "uuid": {"visible": {"value": True}},
            "code": {"visible": {"value": True}},
            "updated_at": {"visible": {"value": True}},
            "updated_by": {"visible": {"value": True}},
        },
    ):
        result = set(sg_entity.all_field_values(project_entity=sg_project).items())

    assert {
        ("linux_path", "/mnt/projects"),
        ("type", "LocalStorage"),
        ("id", 1),
        ("description", None),
        ("cached_display_name", None),
        ("mac_path", "/Volumes/projects"),
        ("created_by", None),
        ("updated_by", None),
        ("created_at", None),
        ("windows_path", "P:\\"),
        ("uuid", None),
        ("code", "primary"),
        ("updated_at", None),
    } == result


def test_fields(sg):
    sg_entity = pysg.SGEntity(sg, 1, "LocalStorage")

    # Mock Mockgun.schema_field_read - the "project_entity" arg is missing in Mockgun.
    with mock.patch.object(
        mockgun.Shotgun,
        "schema_field_read",
        return_value={
            "linux_path": {"visible": {"value": True}},
            "type": {"visible": {"value": True}},
            "id": {"visible": {"value": True}},
            "description": {"visible": {"value": True}},
            "cached_display_name": {"visible": {"value": True}},
            "mac_path": {"visible": {"value": True}},
            "created_at": {"visible": {"value": True}},
            "created_by": {"visible": {"value": True}},
            "windows_path": {"visible": {"value": True}},
            "uuid": {"visible": {"value": True}},
            "code": {"visible": {"value": True}},
            "updated_at": {"visible": {"value": True}},
            "updated_by": {"visible": {"value": True}},
        },
    ):
        result = sg_entity.fields()

    assert {
        "linux_path",
        "type",
        "id",
        "description",
        "cached_display_name",
        "mac_path",
        "created_by",
        "updated_by",
        "created_at",
        "windows_path",
        "uuid",
        "code",
        "updated_at",
    } == {field.name for field in result}
    assert all([isinstance(field, pysg.Field) for field in result])


def test_fields__project(sg):
    sg_entity = pysg.SGEntity(sg, 1, "LocalStorage")
    sg_project = pysg.SGEntity(sg, 1, "Project")

    # Mock Mockgun.schema_field_read - the "project_entity" arg is missing in Mockgun.
    with mock.patch.object(
        mockgun.Shotgun,
        "schema_field_read",
        return_value={
            "linux_path": {"visible": {"value": True}},
            "type": {"visible": {"value": True}},
            "id": {"visible": {"value": True}},
            "description": {"visible": {"value": True}},
            "cached_display_name": {"visible": {"value": True}},
            "mac_path": {"visible": {"value": True}},
            "created_at": {"visible": {"value": True}},
            "created_by": {"visible": {"value": True}},
            "windows_path": {"visible": {"value": True}},
            "uuid": {"visible": {"value": True}},
            "code": {"visible": {"value": True}},
            "updated_at": {"visible": {"value": True}},
            "updated_by": {"visible": {"value": True}},
        },
    ):
        result = sg_entity.fields(project_entity=sg_project)

    assert {
        "linux_path",
        "type",
        "id",
        "description",
        "cached_display_name",
        "mac_path",
        "created_by",
        "updated_by",
        "created_at",
        "windows_path",
        "uuid",
        "code",
        "updated_at",
    } == {field.name for field in result}
    assert all([isinstance(field, pysg.Field) for field in result])


def test_batch_update_dict(sg):
    sg_project = pysg.new_entity(sg, 1, "Project")

    result = sg_project.batch_update_dict({"name": "FooBar"})

    assert {
        "request_type": "update",
        "entity_type": "Project",
        "entity_id": 1,
        "data": {"name": "FooBar"},
    } == result


def test_shotgun_url(sg):
    sg_entity = pysg.SGEntity(sg, 1, "Project")

    assert "https://test.shotgunstudio.com/detail/Project/1" == sg_entity.url


def test_entity_display_name(sg):
    sg_entity = pysg.SGEntity(sg, 1, "CustomEntity01")

    assert "Sprint" == sg_entity.entity_display_name


def test_schema(sg):
    sg_entity = pysg.SGEntity(sg, 1, "Project")

    assert {
        "name": {"editable": False, "value": "Project"},
        "visible": {"editable": False, "value": True},
    } == sg_entity.schema()


def test_field_schemas(sg):
    sg_entity = pysg.SGEntity(sg, 1, "Project")

    result = sg_entity.field_schemas()

    assert "Tank Name" == result["tank_name"].display_name
    assert 67 == len(result)


def test_upload(sg):
    sg_entity = pysg.SGEntity(sg, 1, "Version")

    # Mock shotgun_api3.Shotgun.upload()
    with mock.patch.object(
        mockgun.Shotgun,
        "upload",
        return_value={
            "type": "Attachment",
            "id": 1,
        },
    ):
        result = sg_entity["sg_uploaded_movie"].upload("/path/to/somewhere.mov")

    assert result.type == "Attachment"


def test_download__errors_on_wrong_field_type(sg):
    sg_entity = pysg.SGEntity(sg, 1, "Version")

    with pytest.raises(RuntimeError):
        sg_entity["code"].download("/path/to/somewhere")


def test_download__errors_when_nothing_is_uploaded(sg):
    sg_entity = pysg.SGEntity(sg, 1, "Version")

    with pytest.raises(RuntimeError):
        sg_entity["sg_uploaded_movie"].download("/path/to/somewhere")


def test_download__downloads_to_full_path(sg, tmp_path):
    sg_entity = pysg.SGEntity(sg, 1, "Version")
    sg_entity["sg_uploaded_movie"].set({"id": 1, "type": "Attachment", "name": "some_movie.mov"})
    download_path = tmp_path / "extra_dir" / "somewhere.mov"

    result = sg_entity["sg_uploaded_movie"].download(str(download_path))

    assert result == str(download_path)


def test_download__downloads_to_folder(sg, tmp_path):
    sg_entity = pysg.SGEntity(sg, 1, "Version")
    sg_entity["sg_uploaded_movie"].set({"id": 1, "type": "Attachment", "name": "some_movie.mov"})
    download_path = tmp_path / "extra_dir"

    result = sg_entity["sg_uploaded_movie"].download(str(download_path))

    assert result.startswith(str(download_path))


def test_download__thumbnail_downloads_to_full_path(sg, tmp_path):
    sg_entity = pysg.SGEntity(sg, 1, "Shot")
    sg_entity.thumbnail.set("someVeryLongPayloadString")
    download_path = tmp_path / "extra_dir" / "somewhere.jpg"

    # Mock Mockgun.schema_field_read - the "project_entity" arg is missing in Mockgun.
    with mock.patch.object(
        pyshotgrid.Field,
        "_download_url",
        return_value=str(tmp_path / "extra_dir" / "somewhere.jpg"),
    ):
        result = sg_entity.thumbnail.download(str(download_path))

    assert result == str(download_path)


def test_download__thumbnail_downloads_to_directory_path(sg, tmp_path):
    sg_entity = pysg.SGEntity(sg, 1, "Shot")
    sg_entity.thumbnail.set("someVeryLongPayloadString")
    download_path = tmp_path / "extra_dir"

    # Mock Mockgun.schema_field_read - the "project_entity" arg is missing in Mockgun.
    with mock.patch.object(
        pyshotgrid.Field,
        "_download_url",
        return_value=str(tmp_path / "extra_dir" / "sq111_sh1111_image.jpg"),
    ):
        result = sg_entity.thumbnail.download(str(download_path))

    assert result.startswith(str(download_path))


def test_compare_entities(sg):
    sg_entity_a = pysg.SGEntity(sg, 1, "Project")
    sg_entity_b = pysg.sg_default_entities.SGProject(sg, 1, "Project")

    assert sg_entity_a == sg_entity_b


def test_compare_entities__ids_dont_match(sg):
    sg_entity_a = pysg.SGEntity(sg, 1, "Project")
    sg_entity_b = pysg.SGEntity(sg, 2, "Project")

    assert sg_entity_a != sg_entity_b


def test_compare_entities__entity_types_dont_match(sg):
    sg_entity_a = pysg.SGEntity(sg, 1, "Project")
    sg_entity_b = pysg.SGEntity(sg, 1, "Version")

    assert sg_entity_a != sg_entity_b


def test_compare_entities__sg_instances_dont_match(sg):
    sg_entity_a = pysg.SGEntity(sg, 1, "Project")
    other_sg = mockgun.Shotgun(
        base_url="https://other.shotgunstudio.com",
        script_name="Unittest User",
        api_key="$ome_password",
    )
    sg_entity_b = pysg.SGEntity(other_sg, 1, "Project")

    assert sg_entity_a != sg_entity_b


def test_compare_entities__not_a_sg_entity(sg):
    sg_entity_a = pysg.SGEntity(sg, 1, "Project")

    assert sg_entity_a != 1


def test_publishes__base_filter(sg):
    sg_user = pysg.SGEntity(sg, 1, "HumanUser")

    result = sg_user._publishes(
        base_filter=[["created_by", "is", sg_user.to_dict()]],
    )

    for pub in result:
        assert sg_user == pub["created_by"].get()


def test_publishes__pub_types_string(sg):
    sg_user = pysg.SGEntity(sg, 1, "HumanUser")

    result = sg_user._publishes(pub_types="Alembic Cache")

    for pub in result:
        assert "Alembic Cache" == pub["published_file_type"].get()["code"].get()


def test_publishes__pub_types_list(sg):
    sg_user = pysg.SGEntity(sg, 1, "HumanUser")

    result = sg_user._publishes(pub_types=["Alembic Cache", "Rendered Image"])

    for pub in result:
        assert pub["published_file_type"].get()["code"].get() in [
            "Alembic Cache",
            "Rendered Image",
        ]


def test_publishes__latest(sg):
    sg_user = pysg.SGEntity(sg, 1, "HumanUser")

    result = sg_user._publishes(latest=True, pub_types="Rendered Image")

    for pub in result:
        assert "Rendered Image" == pub["published_file_type"].get()["code"].get()


def test_tasks__name(sg):
    sg_user = pysg.SGEntity(sg, 1, "HumanUser")

    result = sg_user._tasks(names=["comp"])

    for task in result:
        assert "comp" == task.name.get()


def test_tasks__names(sg):
    sg_user = pysg.SGEntity(sg, 1, "HumanUser")

    result = sg_user._tasks(names=["comp", "lighting"])

    for task in result:
        assert task.name.get() in ["comp", "lighting"]


def test_tasks__assignee(sg):
    sg_user = pysg.SGEntity(sg, 1, "HumanUser")

    result = sg_user._tasks(assignee=sg_user)

    for task in result:
        assert sg_user in task["task_assignees"].get()


def test_tasks__assignee_dict(sg):
    sg_user = pysg.SGEntity(sg, 1, "HumanUser")

    result = sg_user._tasks(assignee={"type": "HumanUser", "id": 1})

    for task in result:
        assert sg_user in task["task_assignees"].get()


def test_tasks__entity(sg):
    sg_user = pysg.SGEntity(sg, 1, "HumanUser")
    entity = pysg.SGEntity(sg, 2, "Shot")

    result = sg_user._tasks(entity=entity)

    for task in result:
        assert entity == task["entity"].get()


def test_tasks__entity_errors_if_has_wrong_type(sg):
    sg_user = pysg.SGEntity(sg, 1, "HumanUser")

    with pytest.raises(TypeError):
        # noinspection PyTypeChecker
        sg_user._tasks(entity="wrong entity type")


def test_tasks__entity_dict(sg):
    sg_user = pysg.SGEntity(sg, 1, "HumanUser")
    entity = {"type": "Shot", "id": 2}

    result = sg_user._tasks(entity=entity)

    for task in result:
        assert entity == task["entity"].get().to_dict()


def test_tasks__entity_is_project(sg):
    sg_user = pysg.SGEntity(sg, 1, "HumanUser")
    entity = pysg.SGEntity(sg, 1, "Project")

    result = sg_user._tasks(entity=entity)

    for task in result:
        assert entity == task["project"].get()


def test_tasks__entity_is_project_dict(sg):
    sg_user = pysg.SGEntity(sg, 1, "HumanUser")
    entity = {"type": "Project", "id": 1}

    result = sg_user._tasks(entity=entity)

    for task in result:
        assert entity == task["project"].get().to_dict()


def test_tasks__pipeline_step_dict(sg):
    sg_user = pysg.SGEntity(sg, 1, "HumanUser")
    pipeline_step = {"type": "Step", "id": 1}

    result = sg_user._tasks(pipeline_step=pipeline_step)

    for task in result:
        assert pipeline_step == task["step"].get().to_dict()


def test_tasks__pipeline_step_string(sg):
    sg_user = pysg.SGEntity(sg, 1, "HumanUser")
    pipeline_step = {"type": "Step", "id": 1}

    result = sg_user._tasks(pipeline_step="Compositing")

    for task in result:
        assert pipeline_step == task["step"].get().to_dict()


def test_tasks__pipeline_step_sgentity(sg):
    sg_user = pysg.SGEntity(sg, 1, "HumanUser")
    pipeline_step = pysg.SGEntity(sg, 1, "Step")

    result = sg_user._tasks(pipeline_step=pipeline_step)

    for task in result:
        assert pipeline_step == task["step"].get()


def test_tasks__pipeline_step_errors_if_has_wrong_type(sg):
    sg_user = pysg.SGEntity(sg, 1, "HumanUser")

    with pytest.raises(TypeError):
        # noinspection PyTypeChecker
        sg_user._tasks(pipeline_step=1)


def test_tasks__all_arguments(sg):
    sg_user = pysg.SGEntity(sg, 1, "HumanUser")
    entity = pysg.SGEntity(sg, 1, "Shot")
    pipeline_step = pysg.SGEntity(sg, 1, "Step")

    result = sg_user._tasks(
        names=["comp"], assignee=sg_user, entity=entity, pipeline_step=pipeline_step
    )

    for task in result:
        assert entity == task["entity"].get()
        assert sg_user in task["task_assignees"].get()
        assert pipeline_step == task["step"].get()
        assert "comp" == task.name.get()


def test_versions__entity_takes_dict(sg):
    sg_shot = pysg.SGEntity(sg, 1, "Shot")

    result = sg_shot._versions(entity={"id": 1, "type": "Shot"})

    assert len(result) > 1
    for version in result:
        assert "Version" == version.type
        assert sg_shot == version["entity"].get()


def test_versions__latest(sg):
    sg_shot = pysg.SGEntity(sg, 1, "Shot")

    result = sg_shot._versions(entity={"id": 1, "type": "Shot"}, latest=True)

    assert len(result) == 1
    version = result[0]
    assert "Version" == version.type
    assert sg_shot == version["entity"].get()


def test_versions__entity_errors_with_wrong_type(sg):
    sg_shot = pysg.SGEntity(sg, 1, "Shot")

    with pytest.raises(TypeError):
        # noinspection PyTypeChecker
        sg_shot._versions(entity=1)


def test_versions__pipeline_step_takes_dict(sg):
    sg_shot = pysg.SGEntity(sg, 1, "Shot")
    pipeline_step = {"id": 1, "type": "Step"}

    result = sg_shot._versions(pipeline_step=pipeline_step)

    assert len(result) > 1
    for version in result:
        assert "Version" == version.type
        assert pipeline_step == version["sg_task"].get()["step"].get().to_dict()


def test_versions__pipeline_step_takes_sgentity(sg):
    sg_shot = pysg.SGEntity(sg, 1, "Shot")
    pipeline_step = pysg.SGEntity(sg, 1, "Step")

    result = sg_shot._versions(pipeline_step=pipeline_step)

    assert len(result) > 1
    for version in result:
        assert "Version" == version.type
        assert pipeline_step == version["sg_task"].get()["step"].get()


def test_versions__pipeline_step_takes_name(sg):
    sg_shot = pysg.SGEntity(sg, 1, "Shot")
    pipeline_step = pysg.SGEntity(sg, 1, "Step")

    result = sg_shot._versions(pipeline_step="Compositing")

    assert len(result) > 1
    for version in result:
        assert "Version" == version.type
        assert pipeline_step == version["sg_task"].get()["step"].get()


def test_versions__pipeline_step_errors_with_wrong_type(sg):
    sg_shot = pysg.SGEntity(sg, 1, "Shot")

    with pytest.raises(TypeError):
        # noinspection PyTypeChecker
        sg_shot._versions(pipeline_step=1)
