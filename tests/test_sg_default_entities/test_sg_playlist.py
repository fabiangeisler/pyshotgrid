import pytest

import pyshotgrid.sg_default_entities as sde


def test_name(sg):
    sg_playlist = sde.SGPlaylist(sg, 1)

    result = sg_playlist.name

    assert result.name == "code"


def test_media_url(sg):
    sg_playlist = sde.SGPlaylist(sg, 1)

    result = sg_playlist.media_url

    assert (
        "https://test.shotgunstudio.com/page/media_center?"
        "type=Playlist&id=1&project_id=1" == result
    )


def test_media_url__errors_if_non_project_playlist(sg):
    sg_playlist = sde.SGPlaylist(sg, 3)

    with pytest.raises(RuntimeError):
        # noinspection PyStatementEffect
        _ = sg_playlist.media_url
