import pyshotgrid.sg_default_entities as sde


def test_name(sg):
    sg_project = sde.SGProject(sg, 1)

    result = sg_project.name

    assert result.name == "name"


def test_shots(sg):
    sg_project = sde.SGProject(sg, 1)

    result = sg_project.shots()

    assert len(result) > 0
    for shot in result:
        assert "Shot" == shot.type
        assert sg_project == shot["project"].get()


def test_shots_glob(sg):
    sg_project = sde.SGProject(sg, 1)

    result = sg_project.shots("sq111_*")

    assert len(result) > 0
    for shot in result:
        assert shot["code"].get().startswith("sq111_")


def test_assets(sg):
    sg_project = sde.SGProject(sg, 1)

    result = sg_project.assets()

    assert len(result) > 0
    for asset in result:
        assert "Asset" == asset.type
        assert sg_project == asset["project"].get()


def test_assets_glob(sg):
    sg_project = sde.SGProject(sg, 1)

    result = sg_project.assets("Car*")

    assert len(result) > 0
    for asset in result:
        assert "Car" in asset["code"].get()


def test_playlists(sg):
    sg_project = sde.SGProject(sg, 1)

    result = sg_project.playlists()

    assert len(result) > 0
    for playlist in result:
        assert "Playlist" == playlist.type
        assert sg_project == playlist["project"].get()


def test_people(sg):
    sg_project = sde.SGProject(sg, 1)

    result = sg_project.people()

    assert len(result) > 0
    for person in result:
        assert person.type == "HumanUser"
        assert sg_project in person["projects"].get()


def test_people__all_people(sg):
    sg_project = sde.SGProject(sg, 1)

    result = sg_project.people(only_active=False)

    tmp_status = set()
    assert len(result) > 0
    for person in result:
        tmp_status.add(person["sg_status_list"].get())
        assert person.type == "HumanUser"
        assert sg_project in person["projects"].get()
    # We asset that the returned people include active and deactivated users.
    assert tmp_status == {"act", "dis"}


def test_publishes(sg):
    sg_project = sde.SGProject(sg, 1)

    result = sg_project.publishes()

    assert len(result) > 0
    for pub in result:
        assert pub.type == "PublishedFile"
        assert sg_project == pub["project"].get()


def test_versions(sg):
    sg_project = sde.SGProject(sg, 1)

    result = sg_project.versions()

    assert len(result) > 0
    for versions in result:
        assert versions.type == "Version"
        assert versions["project"].get() == sg_project
