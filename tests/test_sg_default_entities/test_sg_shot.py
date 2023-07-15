import pyshotgrid.sg_default_entities as sde


def test_tasks(sg):
    sg_shot = sde.SGShot(sg, 1)

    result = sg_shot.tasks()

    for task in result:
        assert sg_shot == task["entity"].get()


def test_publishes(sg):
    sg_shot = sde.SGShot(sg, 1)

    result = sg_shot.publishes()

    for pub in result:
        assert sg_shot == pub["entity"].get()
