"""Tests for `pyshotgrid` package."""

from unittest import mock

import pytest
from shotgun_api3.lib import mockgun

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


def test_name(sg):
    sg_project = pysg.new_entity(sg, 1, "Project")
    sg_task = pysg.new_entity(sg, 1, "Task")
    sg_asset = pysg.new_entity(sg, 1, "Asset")

    result_project_name_field = sg_project.name
    result_task_name_field = sg_task.name
    result_asset_name_field = sg_asset.name

    assert "name" == result_project_name_field.name
    assert "content" == result_task_name_field.name
    assert "code" == result_asset_name_field.name


def test_name__errors_when_no_name_field_present(sg):
    sg_entity = pysg.new_entity(sg, 1, "Note")

    with pytest.raises(RuntimeError):
        _ = sg_entity.name


# FIXME Mockgun.update is missing the "multi_entity_update_modes" parameter. We need to patch it
# FIXME to make this test work.
# def test_set(sg):
#     sg_entity = pysg.SGEntity(sg, 'Project', 1)
#     def patched_update(entity_type, entity_id, data, multi_entity_update_modes=None):
#         sg.update(entity_type, entity_id, data)
#
#     with mock.patch.object(mockgun.Shotgun, "update", new_callable=patched_update):
#         sg_entity.set({'code': 'Test Name', 'tank_name': 'tn'})
#
#     assert ({'code': 'Test Name', 'tank_name': 'tn'},
#                      sg_entity.get(['code', 'tank_name']))
#     # Cleanup
#     sg_entity.set({'code': 'Test Project', 'tank_name': 'tp'})


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
