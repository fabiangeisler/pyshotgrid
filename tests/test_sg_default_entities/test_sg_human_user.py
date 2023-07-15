"""Tests for `pyshotgrid` default entities."""
import pyshotgrid.sg_default_entities as sde


def test_tasks(sg):
    sg_user = sde.SGHumanUser(sg, 1)

    result = sg_user.tasks()

    for task in result:
        assert sg_user in task["task_assignees"].get()


def test_publishes(sg):
    sg_user = sde.SGHumanUser(sg, 1)

    result = sg_user.publishes()

    for pub in result:
        assert sg_user == pub["created_by"].get()
