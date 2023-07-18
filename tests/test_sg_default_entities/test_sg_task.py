import pyshotgrid.sg_default_entities as sde


def test_name(sg):
    sg_task = sde.SGTask(sg, 1)

    result = sg_task.name.get()

    assert "comp" == result


def test_publishes(sg):
    sg_task = sde.SGTask(sg, 1)

    result = sg_task.publishes()

    assert len(result) > 0
    for pub in result:
        assert pub.type == "PublishedFile"
        assert sg_task == pub["task"].get()


def test_versions(sg):
    sg_task = sde.SGTask(sg, 1)

    result = sg_task.versions()

    assert len(result) > 0
    for versions in result:
        assert versions.type == "Version"
        assert versions["sg_task"].get() == sg_task
