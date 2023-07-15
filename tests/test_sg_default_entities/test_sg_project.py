import pyshotgrid.sg_default_entities as sde


def test_shots(sg):
    sg_project = sde.SGProject(sg, 1)

    result = sg_project.shots()

    for shot in result:
        assert "Shot" == shot.type
        assert sg_project == shot["project"].get()


def test_shots_glob(sg):
    sg_project = sde.SGProject(sg, 1)

    result = sg_project.shots("sq111_*")

    for shot in result:
        assert shot["code"].get().startswith("sq111_")


def test_assets(sg):
    sg_project = sde.SGProject(sg, 1)

    result = sg_project.assets()

    for asset in result:
        assert "Asset" == asset.type
        assert sg_project == asset["project"].get()


def test_assets_glob(sg):
    sg_project = sde.SGProject(sg, 1)

    result = sg_project.assets("Car*")

    for asset in result:
        assert "Car" in asset["code"].get()


def test_playlists(sg):
    sg_project = sde.SGProject(sg, 1)

    result = sg_project.playlists()

    for playlist in result:
        assert "Playlist" == playlist.type
        assert sg_project == playlist["project"].get()


def test_people(sg):
    sg_project = sde.SGProject(sg, 1)

    result = sg_project.people()

    for person in result:
        assert sg_project in person["projects"].get()


def test_people_additional_filters(sg):
    sg_project = sde.SGProject(sg, 1)

    result = sg_project.people(additional_sg_filter=[["firstname", "is", "Alice"]])

    for person in result:
        assert sg_project in person["projects"].get()
        assert "Alice" == person["firstname"].get()


def test_publishes(sg):
    sg_project = sde.SGProject(sg, 1)

    result = sg_project.publishes()

    for pub in result:
        assert sg_project == pub["project"].get()
