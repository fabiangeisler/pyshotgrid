"""
This module collects all default pyshotgrid custom entities.
"""
import fnmatch
import typing
from typing import Any, Dict, List, Optional, Type, Union  # noqa: F401

if typing.TYPE_CHECKING:  # pragma: no cover
    import shotgun_api3  # noqa: F401

    from .core import Field  # noqa: F401

from .core import SGEntity, new_entity


class SGProject(SGEntity):
    """
    An instance of this class represents a single Project entity in ShotGrid.

    .. Note::

        Try to avoid creating instances of this class in production code and
        use the :py:meth:`pyshotgrid.new_entity <pyshotgrid.core.new_entity>`
        method instead. This will make sure that you always get the correct
        entity class to work with.
    """

    DEFAULT_SG_ENTITY_TYPE = "Project"

    def shots(self, glob_pattern=None):
        # type: (Optional[str]) -> List[SGEntity]
        """
        :param glob_pattern: A glob to match the shots to return. For example
                             `TEST_01_*` would return all shots that start with `TEST_01_`.
        :return: All the shots from this project.
        """
        sg_shots = self.sg.find("Shot", [["project", "is", self.to_dict()]], ["code"])
        if glob_pattern is not None:
            return [
                new_entity(self._sg, sg_shot)
                for sg_shot in sg_shots
                if fnmatch.fnmatchcase(sg_shot["code"], glob_pattern)
            ]
        else:
            return [new_entity(self._sg, sg_shot) for sg_shot in sg_shots]

    def assets(self, glob_pattern=None):
        # type: (Optional[str]) -> List[SGEntity]
        """
        :param glob_pattern: A glob to match the assets to return. For example
                            `TEST_*` would return all assets that start with `TEST_`.
        :return: All the assets from this project.
        """
        sg_assets = self.sg.find("Asset", [["project", "is", self.to_dict()]], ["code"])
        if glob_pattern is not None:
            return [
                new_entity(self._sg, sg_asset)
                for sg_asset in sg_assets
                if fnmatch.fnmatchcase(sg_asset["code"], glob_pattern)
            ]
        else:
            return [new_entity(self._sg, sg_asset) for sg_asset in sg_assets]

    def publishes(
        self,
        pub_types=None,  # type: Optional[Union[str,List[str]]]
        latest=False,  # type: bool
    ):
        # type: (...) -> List[SGEntity]
        """
        :param pub_types: The names of the Publish File Types to return.
        :param latest: Whether to get the "latest" publishes or not. This uses the
          same logic as the tk-multi-loader2 app which is as follows:

            - group all publishes with the same "name" field together
            - from these get the publishes with the highest "version_number" field
            - if there are publishes with the same "name" and "version_number" the
              newest one wins.
        :return: All published files from this project.
        """
        return self._publishes(
            base_filter=[["project", "is", self.to_dict()]],
            pub_types=pub_types,
            latest=latest,
        )

    def people(self, only_active=True):
        # type: (bool) -> List[SGEntity]
        """
        :param only_active: Whether to list only active people or all the people.
        :return: All HumanUsers assigned to this project.
        """
        sg_filter = [["projects", "is", self.to_dict()]]
        if only_active:
            sg_filter.append(["sg_status_list", "is", "act"])

        return [
            new_entity(self._sg, sg_user)
            for sg_user in self._sg.find("HumanUser", sg_filter)
        ]

    def playlists(self):
        # type: () -> List[SGEntity]
        """
        :return: All playlists attached to this project.
        """
        return [
            new_entity(self._sg, sg_playlist)
            for sg_playlist in self._sg.find(
                "Playlist", [["project", "is", self.to_dict()]]
            )
        ]

    def versions(
        self,
        user=None,  # type: Optional[Union[Dict[str,Any],SGEntity]]
        pipeline_step=None,  # type: Optional[Union[str,Dict[str,Any],SGEntity]]
        latest=False,  # type: bool
    ):
        # type: (...) -> List[SGEntity]
        """
        :param user: The artist assigned to the Versions.
        :param pipeline_step: Name, short name or entity object or the Pipeline Step to filter by.
        :param latest: Whether to return only the latest Version per link/entity.
        :returns: A list of Versions
        """
        return self._versions(
            entity=self,
            user=user,
            pipeline_step=pipeline_step,
            latest=latest,
        )


class SGShot(SGEntity):
    """
    An instance of this class represents a single Shot entity in ShotGrid.

    .. Note::

        Try to avoid creating instances of this class in production code and
        use the :py:meth:`pyshotgrid.new_entity <pyshotgrid.core.new_entity>`
        method instead. This will make sure that you always get the correct
        entity class to work with.
    """

    DEFAULT_SG_ENTITY_TYPE = "Shot"

    def publishes(
        self,
        pub_types=None,  # type: Optional[Union[str,List[str]]]
        latest=False,  # type: bool
    ):
        # type: (...) -> List[SGEntity]
        """
        :param pub_types: The names of the Publish File Types to return.
        :param latest: Whether to get the "latest" publishes or not. This uses the
                       same logic as the tk-multi-loader2 app which is as follows:

                         - group all publishes with the same "name" field together
                         - from these get the publishes with the highest "version_number" field
                         - if there are publishes with the same "name" and "version_number" the
                           newest one wins.
        :return: All published files from this shot.
        """
        return self._publishes(
            base_filter=[["entity", "is", self.to_dict()]],
            pub_types=pub_types,
            latest=latest,
        )

    def tasks(
        self,
        names=None,  # type: Optional[List[str]]
        assignee=None,  # type: Optional[Union[Dict[str,Any],SGEntity]]
        pipeline_step=None,  # type: Optional[Union[str,Dict[str,Any],SGEntity]]
    ):
        # type: (...) -> List[SGEntity]
        """
        :param names: The names of Tasks to return.
        :param assignee: The assignee of the Tasks to return.
        :param pipeline_step: Name, short name or entity object
                              or the Pipeline Step to filter by.
        :returns: A list of Tasks.
        """
        return self._tasks(
            names=names,
            entity=self.to_dict(),
            assignee=assignee,
            pipeline_step=pipeline_step,
        )

    def versions(
        self,
        user=None,  # type: Optional[Union[Dict[str,Any],SGEntity]]
        pipeline_step=None,  # type: Optional[Union[str,Dict[str,Any],SGEntity]]
        latest=False,  # type: bool
    ):
        # type: (...) -> List[SGEntity]
        """
        :param user: The artist assigned to the Versions.
        :param pipeline_step: Name, short name or entity object or the Pipeline Step to filter by.
        :param latest: Whether to return only the latest Version per link/entity.
        :returns: A list of Versions
        """
        return self._versions(
            entity=self,
            user=user,
            pipeline_step=pipeline_step,
            latest=latest,
        )


class SGAsset(SGEntity):
    """
    An instance of this class represents a single Asset entity in ShotGrid.

    .. Note::

        Try to avoid creating instances of this class in production code and
        use the :py:meth:`pyshotgrid.new_entity <pyshotgrid.core.new_entity>`
        method instead. This will make sure that you always get the correct
        entity class to work with.
    """

    DEFAULT_SG_ENTITY_TYPE = "Asset"

    def publishes(
        self,
        pub_types=None,  # type: Optional[Union[str,List[str]]]
        latest=False,  # type: bool
    ):
        # type: (...) -> List[SGEntity]
        """
        :param pub_types: The names of the Publish File Types to return.
        :param latest: Whether to get the "latest" publishes or not. This uses the
                       same logic as the tk-multi-loader2 app which is as follows:

                         - group all publishes with the same "name" field together
                         - from these get the publishes with the highest "version_number" field
                         - if there are publishes with the same "name" and "version_number" the
                           newest one wins.
        :return: All published files from this asset.
        """
        return self._publishes(
            base_filter=[["entity", "is", self.to_dict()]],
            pub_types=pub_types,
            latest=latest,
        )

    def tasks(
        self,
        names=None,  # type: Optional[List[str]]
        assignee=None,  # type: Optional[Union[Dict[str,Any],SGEntity]]
        pipeline_step=None,  # type: Optional[Union[str,Dict[str,Any],SGEntity]]
    ):
        # type: (...) -> List[SGEntity]
        """
        :param names: The names of Tasks to return.
        :param assignee: The assignee of the tasks to return.
        :param pipeline_step: Name, short name or entity object
                              or the Pipeline Step to filter by.
        :returns: A list of Tasks.
        """
        return self._tasks(
            names=names,
            entity=self.to_dict(),
            assignee=assignee,
            pipeline_step=pipeline_step,
        )

    def versions(
        self,
        user=None,  # type: Optional[Union[Dict[str,Any],SGEntity]]
        pipeline_step=None,  # type: Optional[Union[str,Dict[str,Any],SGEntity]]
        latest=False,  # type: bool
    ):
        # type: (...) -> List[SGEntity]
        """
        :param user: The artist assigned to the Versions.
        :param pipeline_step: Name, short name or entity object or the Pipeline Step to filter by.
        :param latest: Whether to return only the latest Version per link/entity.
        :returns: A list of Versions
        """
        return self._versions(
            entity=self,
            user=user,
            pipeline_step=pipeline_step,
            latest=latest,
        )


class SGTask(SGEntity):
    """
    An instance of this class represents a single Task entity in ShotGrid.

    .. Note::

        Try to avoid creating instances of this class in production code and
        use the :py:meth:`pyshotgrid.new_entity <pyshotgrid.core.new_entity>`
        method instead. This will make sure that you always get the correct
        entity class to work with.
    """

    DEFAULT_SG_ENTITY_TYPE = "Task"

    @property
    def name(self):
        # type: () -> Field
        """
        :return: The field that represents the name of the Task.
        """
        return self["content"]

    def publishes(
        self,
        pub_types=None,  # type: Optional[Union[str,List[str]]]
        latest=False,  # type: bool
    ):
        # type: (...) -> List[SGEntity]
        """
        :param pub_types: The names of the Publish File Types to return.
        :param latest: Whether to get the "latest" publishes or not. This uses the
                       same logic as the tk-multi-loader2 app which is as follows:

                        - group all publishes with the same "name" field together
                        - from these get the publishes with the highest "version_number" field
                        - if there are publishes with the same "name" and "version_number" the
                          newest one wins.
        :return: All published files from this shot.
        """
        return self._publishes(
            base_filter=[["task", "is", self.to_dict()]],
            pub_types=pub_types,
            latest=latest,
        )

    def versions(
        self,
        user=None,  # type: Optional[Union[Dict[str,Any],SGEntity]]
        pipeline_step=None,  # type: Optional[Union[str,Dict[str,Any],SGEntity]]
        latest=False,  # type: bool
    ):
        # type: (...) -> List[SGEntity]
        """
        :param user: The artist assigned to the Versions.
        :param pipeline_step: Name, short name or entity object or the Pipeline Step to filter by.
        :param latest: Whether to return only the latest Version per link/entity.
        :returns: A list of Versions
        """
        return self._versions(
            entity=self,
            user=user,
            pipeline_step=pipeline_step,
            latest=latest,
        )


class SGPublishedFile(SGEntity):
    """
    An instance of this class represents a single PublishedFile entity in ShotGrid.

    .. Note::

        Try to avoid creating instances of this class in production code and
        use the :py:meth:`pyshotgrid.new_entity <pyshotgrid.core.new_entity>`
        method instead. This will make sure that you always get the correct
        entity class to work with.
    """

    DEFAULT_SG_ENTITY_TYPE = "PublishedFile"

    def is_latest(self):
        # type: () -> bool
        """
        :return: Whether this published file is the latest of its kind.
        """
        return self.get_latest() == self

    def get_latest(self):
        # type: () -> SGEntity
        """
        :return: The latest published file of its kind (which might be this same entity).
        """
        return self.get_all_publishes()[-1]

    def get_next_publishes(self):
        # type: () -> List[SGEntity]
        """
        :return: The next publishes after this publish.
        """
        all_publishes = self.get_all_publishes()
        index = all_publishes.index(self)
        return all_publishes[index + 1 :]

    def get_previous_publishes(self):
        # type: () -> List[SGEntity]
        """
        :return: The previous publishes before this publish.
        """
        all_publishes = self.get_all_publishes()
        index = all_publishes.index(self)
        return all_publishes[:index]

    def get_all_publishes(self):
        # type: () -> List[SGEntity]
        """
        :return: A list of all the published file versions from lowest to highest version number.
        """
        this_publish = self.get(
            ["entity", "published_file_type", "name"], raw_values=True
        )
        sg_publishes = self.sg.find(
            "PublishedFile",
            [
                ["entity", "is", this_publish["entity"]],
                ["published_file_type", "is", this_publish["published_file_type"]],
                ["name", "is", this_publish["name"]],
            ],
            ["name", "version_number", "created_at"],
        )

        # sort them by date and than by version_number which sorts the latest publish to the
        # last position.
        sg_publishes.sort(key=lambda pub: (pub["created_at"], pub["version_number"]))

        return [new_entity(self._sg, sg_publish) for sg_publish in sg_publishes]


class SGVersion(SGEntity):
    """
    An instance of this class represents a single Version entity in ShotGrid.

    .. Note::

        Try to avoid creating instances of this class in production code and
        use the :py:meth:`pyshotgrid.new_entity <pyshotgrid.core.new_entity>`
        method instead. This will make sure that you always get the correct
        entity class to work with.
    """

    DEFAULT_SG_ENTITY_TYPE = "Version"

    # TODO get note threads


class SGPlaylist(SGEntity):
    """
    An instance of this class represents a single Playlist entity in ShotGrid.

    .. Note::

        Try to avoid creating instances of this class in production code and
        use the :py:meth:`pyshotgrid.new_entity <pyshotgrid.core.new_entity>`
        method instead. This will make sure that you always get the correct
        entity class to work with.
    """

    DEFAULT_SG_ENTITY_TYPE = "Playlist"

    @property
    def media_url(self):
        # type: () -> str
        """
        :return: The Media center URL for this playlist.
        :raises:
            :RuntimeError: When this playlist is not attached to a project.
        """
        sg_project = self["project"].get()
        if sg_project is None:
            raise RuntimeError(
                'Cannot get media URL for playlist "{}"'
                ", because it is not attached to a project.".format(self.id)
            )
        # Example URL:
        # https://example.shotgunstudio.com/page/media_center?type=Playlist&id=123&project_id=456
        return "{}/page/media_center?type={}&id={}&project_id={}".format(
            self.sg.base_url, self._type, self._id, sg_project["id"].get()
        )


class SGHumanUser(SGEntity):
    """
    An instance of this class represents a single HumanUser entity in ShotGrid.

    .. Note::

        Try to avoid creating instances of this class in production code and
        use the :py:meth:`pyshotgrid.new_entity <pyshotgrid.core.new_entity>`
        method instead. This will make sure that you always get the correct
        entity class to work with.
    """

    DEFAULT_SG_ENTITY_TYPE = "HumanUser"

    # TODO time logs

    def versions(
        self,
        entity=None,  # type: Optional[Union[Dict[str,Any],SGEntity]]
        pipeline_step=None,  # type: Optional[Union[str,Dict[str,Any],SGEntity]]
        latest=False,  # type: bool
    ):
        # type: (...) -> List[SGEntity]
        """
        :param entity: entity to filter by eg. (Shot, Asset, Project, Task...).
        :param pipeline_step: Name, short name or entity object or the Pipeline Step to filter by.
        :param latest: Whether to return only the latest Version per link/entity.
        :returns: A list of Versions
        """
        return self._versions(
            entity=entity,
            user=self,
            pipeline_step=pipeline_step,
            latest=latest,
        )

    def tasks(
        self,
        names=None,  # type: Optional[List[str]]
        entity=None,  # type: Optional[Union[Dict[str,Any],SGEntity]]
        pipeline_step=None,  # type: Optional[Union[str,Dict[str,Any],SGEntity]]
    ):
        # type: (...) -> List[SGEntity]
        """
        :param names: The names of Tasks to return.
        :param entity: entity to filter by eg. (Shot, Asset, Project,...).
        :param pipeline_step: Name, short name or entity object or the Pipeline Step to filter by.
        :returns: A list of Tasks
        """
        return self._tasks(
            names=names,
            assignee=self.to_dict(),
            entity=entity,
            pipeline_step=pipeline_step,
        )

    def publishes(
        self,
        pub_types=None,  # type: Optional[Union[str,List[str]]]
        latest=False,  # type: bool
    ):
        # type: (...) -> List[SGEntity]
        """
        :param pub_types: The names of the Publish File Types to return.
        :param latest: Whether to get the "latest" publishes or not. This uses the
                       same logic as the tk-multi-loader2 app which is as follows:

                        - group all publishes with the same "name" field together
                        - from these get the publishes with the highest "version_number" field
                        - if there are publishes with the same "name" and "version_number" the
                          newest one wins.
        :return: All published files from this shot.
        """
        return self._publishes(
            base_filter=[["created_by", "is", self.to_dict()]],
            pub_types=pub_types,
            latest=latest,
        )
