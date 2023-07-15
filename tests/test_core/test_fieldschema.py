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
