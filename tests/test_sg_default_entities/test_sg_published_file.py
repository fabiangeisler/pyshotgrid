import pyshotgrid.sg_default_entities as sde


def test_is_latest__false(sg):
    sg_publish = sde.SGPublishedFile(sg, 1)

    result = sg_publish.is_latest()

    assert not result


def test_is_latest__true(sg):
    sg_publish = sde.SGPublishedFile(sg, 5)

    result = sg_publish.is_latest()

    assert result


def test_get_latest_publish__is_already_latest(sg):
    sg_publish = sde.SGPublishedFile(sg, 5)

    result = sg_publish.get_latest_publish()

    assert sg_publish == result


def test_get_latest_publish(sg):
    sg_publish = sde.SGPublishedFile(sg, 1)
    latest_sg_publish = sde.SGPublishedFile(sg, 5)

    result = sg_publish.get_latest_publish()

    assert latest_sg_publish == result


def test_get_all_publishes(sg):
    sg_publishes = [sde.SGPublishedFile(sg, i) for i in range(1, 6)]

    result = sg_publishes[0].get_all_publishes()

    assert sg_publishes == result


def test_get_next_publishes(sg):
    sg_publish = sde.SGPublishedFile(sg, 3)
    result_sg_publishes = [sde.SGPublishedFile(sg, i) for i in range(4, 6)]

    result = sg_publish.get_next_publishes()

    assert result_sg_publishes == result


def test_get_previous_publishes(sg):
    sg_publish = sde.SGPublishedFile(sg, 3)
    result_sg_publishes = [sde.SGPublishedFile(sg, i) for i in range(1, 3)]

    result = sg_publish.get_previous_publishes()

    assert result_sg_publishes == result
