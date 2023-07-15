import pyshotgrid.sg_default_entities as sde


def test_tasks(sg):
    sg_asset = sde.SGAsset(sg, 1)

    result = sg_asset.tasks()

    for task in result:
        assert sg_asset == task["entity"].get()


def test_publishes(sg):
    sg_asset = sde.SGAsset(sg, 1)

    result = sg_asset.publishes()

    for pub in result:
        assert sg_asset == pub["entity"].get()
