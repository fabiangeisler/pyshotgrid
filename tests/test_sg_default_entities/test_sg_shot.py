import pyshotgrid.sg_default_entities as sde


def test_name(sg):
    sg_shot = sde.SGShot(sg, 1)

    result = sg_shot.name

    assert result.name == "code"


def test_tasks(sg):
    sg_shot = sde.SGShot(sg, 1)

    result = sg_shot.tasks()

    assert len(result) > 0
    for task in result:
        assert task.type == "Task"
        assert sg_shot == task["entity"].get()


def test_publishes(sg):
    sg_shot = sde.SGShot(sg, 1)

    result = sg_shot.publishes()

    assert len(result) > 0
    for pub in result:
        assert pub.type == "PublishedFile"
        assert sg_shot == pub["entity"].get()


def test_versions(sg):
    sg_shot = sde.SGShot(sg, 1)

    result = sg_shot.versions()

    assert len(result) > 0
    for versions in result:
        assert versions.type == "Version"
        assert versions["entity"].get() == sg_shot
