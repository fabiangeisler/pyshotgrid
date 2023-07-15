import pyshotgrid.sg_default_entities as sde


def test_name(sg):
    sg_task = sde.SGTask(sg, 1)

    result = sg_task.name.get()

    assert "comp" == result


def test_publishes(sg):
    sg_task = sde.SGTask(sg, 1)

    result = sg_task.publishes()

    for pub in result:
        assert sg_task == pub["task"].get()
