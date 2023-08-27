"""Tests for `pyshotgrid.core.FieldSchema` class."""

import pyshotgrid as pysg


def test_display_name(sg):
    sg_field_schema = pysg.core.FieldSchema(sg, "Project", "name")

    result = sg_field_schema.display_name

    assert "Project Name" == result


def test_data_type(sg):
    sg_field_schema = pysg.core.FieldSchema(sg, "Project", "name")

    result = sg_field_schema.data_type

    assert "text" == result


def test_description(sg):
    sg_field_schema = pysg.core.FieldSchema(sg, "Project", "name")

    result = sg_field_schema.description

    assert "" == result


def test_string_representation(sg):
    sg_field_schema = pysg.core.FieldSchema(sg, "Project", "name")

    result = str(sg_field_schema)

    assert "FieldSchema - name - Entity: Project" == result


def test_custom_metadata(sg):
    sg_field_schema = pysg.core.FieldSchema(sg, "Project", "name")

    result = sg_field_schema.custom_metadata

    assert "" == result


def test_valid_types(sg):
    sg_field_schema = pysg.core.FieldSchema(sg, "Version", "user")

    result = sg_field_schema.valid_types

    assert result == ["HumanUser", "ApiUser", "Group"]


def test_properties(sg):
    sg_field_schema = pysg.core.FieldSchema(sg, "Version", "sg_status_list")

    result = sg_field_schema.properties

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
