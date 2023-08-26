"""Tests for `pyshotgrid` core.Field class."""
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
    assert result.field_name == "name"
    assert result.entity_type == "Project"


def test_valid_types(sg):
    sg_version = pysg.new_entity(sg, 1, "Version")
    sg_user_field = pysg.core.Field("user", sg_version)

    result = sg_user_field.valid_types

    assert result == ["HumanUser", "ApiUser", "Group"]


def test_properties(sg):
    sg_version = pysg.new_entity(sg, 1, "Version")
    sg_status_field = pysg.core.Field("sg_status_list", sg_version)

    result = sg_status_field.properties

    assert result == {
        "default_value": {"editable": True, "value": "wtg"},
        "display_values": {
            "editable": False,
            "value": {
                "4k": "4k",
                "ab": "Awaiting Brief",
                "animre": "animrefine",
                "apr": "Approved",
                "ato": "Awaiting TO",
                "bid": "Bid",
                "cbb": "CBB",
                "change": "requires changes",
                "client": "Client Approved",
                "clnt": "Approved Client",
                "dlvr": "Delivered",
                "exr": "Send EXR",
                "f": "Final",
                "fin": "Final",
                "fp": "Final Pending",
                "hld": "On Hold",
                "intap": "Internally approved",
                "ip": "In Progress",
                "lap": "Lead Approved",
                "late": "Late",
                "na": "N/A",
                "nbg": "awaiting BG",
                "np4": "NetflixP4",
                "oat": "Omit after turnover",
                "omt": "Omit",
                "out": "With Outsourcing",
                "paw": "Present as WIP",
                "pc": "Present to Client",
                "pcf": "Pending Client Feedback",
                "pe4": "Pending 4K",
                "pel": "Pending Element",
                "pf": "Potential Final",
                "plsh": "Polish",
                "pre": "Presented",
                "rdy": "Ready to Start",
                "rev": "Pending Review",
                "rfa": "Ready for Anim",
                "rfc": "Ready for Comp",
                "rfd": "Ready For DMP",
                "rfl": "Ready for Light",
                "rfm": "Ready for Matchmove",
                "rft": "Ready For Tech",
                "rfx": "Ready for FX",
                "rsk": "At Risk",
                "sappr": "Supervisor Approved",
                "sd": "Send DPX",
                "sha": "shared",
                "ste": "Sent to Editorial",
                "tca": "TC Approved",
                "tcp": "TechCheck Pending",
                "temp": "temp approved",
                "tr": "Tech Error",
                "tst": "Testing",
                "vwd": "Viewed",
                "wtg": "Waiting to Start",
            },
        },
        "hidden_values": {"editable": False, "value": []},
        "summary_default": {"editable": True, "value": "status_list"},
        "valid_values": {
            "editable": True,
            "value": [
                "ato",
                "bid",
                "pel",
                "wtg",
                "rdy",
                "ip",
                "intap",
                "rev",
                "clnt",
                "apr",
                "pcf",
                "pf",
                "fp",
                "f",
                "tcp",
                "dlvr",
                "fin",
                "hld",
                "omt",
                "na",
                "out",
                "cbb",
                "temp",
                "rsk",
                "late",
                "pre",
                "paw",
                "tca",
                "client",
                "change",
                "sappr",
                "nbg",
                "ab",
                "ste",
                "rfa",
                "rfl",
                "rfx",
                "rfc",
                "rfm",
                "rfd",
                "rft",
                "sd",
                "oat",
                "tst",
                "lap",
                "pe4",
                "exr",
                "np4",
                "plsh",
                "vwd",
                "4k",
                "tr",
                "pc",
                "sha",
                "animre",
            ],
        },
    }


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
