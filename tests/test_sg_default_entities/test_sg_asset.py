import pyshotgrid.sg_default_entities as sde


def test_tasks(sg):
    sg_asset = sde.SGAsset(sg, 1)

    result = sg_asset.tasks()

    assert len(result) > 0
    for task in result:
        assert task.type == "Task"
        assert sg_asset == task["entity"].get()


def test_publishes(sg):
    sg_asset = sde.SGAsset(sg, 1)

    result = sg_asset.publishes()

    assert len(result) > 0
    for pub in result:
        assert pub.type == "PublishedFile"
        assert sg_asset == pub["entity"].get()


def test_versions(sg):
    sg_asset = sde.SGAsset(sg, 1)

    result = sg_asset.versions()

    assert len(result) > 0
    for versions in result:
        assert versions.type == "Version"
        assert versions["entity"].get() == sg_asset
