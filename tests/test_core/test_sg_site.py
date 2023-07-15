"""Tests for `pyshotgrid` SGSite class."""
from unittest import mock

import pytest
from shotgun_api3.lib import mockgun

import pyshotgrid as pysg
import pyshotgrid.sg_default_entities as sde


def test_project(sg):
    sg_site = pysg.SGSite(sg)

    # Mock Mockgun.Shotgun.find - the "include_archived_projects" arg is missing in Mockgun.
    with mock.patch.object(
        mockgun.Shotgun,
        "find",
        return_value=[
            {
                "type": "Project",
                "id": 1,
            }
        ],
    ):
        result = sg_site.project(1)

    assert result.type == "Project"
    assert result.id == 1


def test_project__can_be_none(sg):
    sg_site = pysg.SGSite(sg)

    # Mock Mockgun.Shotgun.find - the "include_archived_projects" arg is missing in Mockgun.
    with mock.patch.object(mockgun.Shotgun, "find", return_value=[]):
        result = sg_site.project(11111)

    assert result is None


def test_projects(sg):
    sg_site = pysg.SGSite(sg)

    # Mock Mockgun.Shotgun.find - the "include_archived_projects" arg is missing in Mockgun.
    with mock.patch.object(
        mockgun.Shotgun,
        "find",
        return_value=[
            {
                "type": "Project",
                "id": 1,
                "tank_name": "tpa",
                "name": "Test Project A",
            },
            {
                "type": "Project",
                "id": 2,
                "tank_name": "tpb",
                "name": "Test Project B",
            },
        ],
    ):
        result = sg_site.projects(["tpa", "Test Project B"])

    for project in result:
        assert project.type == "Project"
        assert project.id in [1, 2]


def test_create(sg):
    sg_site = pysg.SGSite(sg)

    result = sg_site.create("Asset", {"code": "sg_site_create_test_asset"})

    assert result.type == "Asset"
    assert result["code"].get() == "sg_site_create_test_asset"

    # Cleanup
    sg.delete(result.type, result.id)


def test_find(sg):
    sg_site = pysg.SGSite(sg)

    # Mock Mockgun.Shotgun.find - the "include_archived_projects" arg is missing in Mockgun.
    with mock.patch.object(
        mockgun.Shotgun,
        "find",
        return_value=[
            {
                "type": "Asset",
                "id": 2,
            },
            {
                "type": "Asset",
                "id": 3,
            },
        ],
    ):
        result = sg_site.find("Asset", [["code", "contains", "Car"]])

    for asset in result:
        assert asset.type == "Asset"
        assert "Car" in asset["code"].get()


def test_find_one(sg):
    sg_site = pysg.SGSite(sg)

    # Mock Mockgun.Shotgun.find - the "include_archived_projects" arg is missing in Mockgun.
    with mock.patch.object(
        mockgun.Shotgun,
        "find",
        return_value=[
            {
                "type": "Asset",
                "id": 1,
            }
        ],
    ):
        result = sg_site.find_one("Asset", [["code", "contains", "Tree"]])

    assert result.type == "Asset"
    assert "Tree" in result["code"].get()


def test_find_one__returns_none_when_nothing_found(sg):
    sg_site = pysg.SGSite(sg)

    # Mock Mockgun.Shotgun.find - the "include_archived_projects" arg is missing in Mockgun.
    with mock.patch.object(mockgun.Shotgun, "find", return_value=[]):
        result = sg_site.find_one("Asset", [["code", "contains", "Not existent name"]])

    assert result is None


def test_people(sg):
    sg_site = pysg.SGSite(sg)

    result = sg_site.people()

    assert 3 == len(result)
    assert isinstance(result[0], sde.SGHumanUser)


def test_pipeline_configuration(sg):
    sg_site = pysg.SGSite(sg)

    result = sg_site.pipeline_configuration()

    assert isinstance(result, sde.SGEntity)


def test_pipeline_configuration__by_name(sg):
    sg_site = pysg.SGSite(sg)

    result = sg_site.pipeline_configuration(name_or_id="Primary")

    assert isinstance(result, sde.SGEntity)
    assert "Primary" == result["code"].get()


def test_pipeline_configuration__returns_none_when_nothing_found(sg):
    sg_site = pysg.SGSite(sg)

    result = sg_site.pipeline_configuration(name_or_id="Not existent config")

    assert result is None


def test_pipeline_configuration__by_id(sg):
    sg_site = pysg.SGSite(sg)

    result = sg_site.pipeline_configuration(name_or_id=1)

    assert isinstance(result, sde.SGEntity)
    assert 1 == result.id


def test_pipeline_configuration__returns_none_when_nothing_matches(sg):
    sg_site = pysg.SGSite(sg)

    result = sg_site.pipeline_configuration(name_or_id=11111)

    assert result is None


def test_pipeline_configuration__by_project(sg):
    sg_project = pysg.new_entity(sg, 1, "Project")
    sg_site = pysg.SGSite(sg)

    result = sg_site.pipeline_configuration(project=sg_project)

    assert isinstance(result, sde.SGEntity)
    assert sg_project == result["project"].get()


def test_pipeline_configuration__by_project_dict(sg):
    sg_project = {"id": 1, "type": "Project"}
    sg_site = pysg.SGSite(sg)

    result = sg_site.pipeline_configuration(project=sg_project)

    assert result.type == "PipelineConfiguration"
    assert sg_project == result["project"].get().to_dict()


def test_pipeline_configuration__invalid_project_raises_error(sg):
    sg_site = pysg.SGSite(sg)

    with pytest.raises(ValueError):
        # noinspection PyTypeChecker
        _ = sg_site.pipeline_configuration(project=1)


def test_entity_field_schemas(sg):
    sg_site = pysg.SGSite(sg)

    result = sg_site.entity_field_schemas()

    assert isinstance(result["Project"]["code"], pysg.FieldSchema)


def test_comparison(sg):
    sg_site_a = pysg.SGSite(sg)
    sg_site_b = pysg.SGSite(sg)

    assert sg_site_a == sg_site_b


def test_comparison__inequality(sg):
    sg_site_a = pysg.SGSite(sg)
    other_sg = mockgun.Shotgun(
        base_url="https://other.shotgunstudio.com",
        script_name="Unittest User",
        api_key="$ome_password",
    )
    sg_site_b = pysg.SGSite(other_sg)

    assert sg_site_a != sg_site_b


def test_comparison__wrong_type(sg):
    sg_site_a = pysg.SGSite(sg)

    assert sg_site_a != 1
