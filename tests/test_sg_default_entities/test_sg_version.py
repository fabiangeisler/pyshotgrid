import pyshotgrid.sg_default_entities as sde


def test_name(sg):
    sg_version = sde.SGVersion(sg, 1)

    result = sg_version.name

    assert result.name == "code"
