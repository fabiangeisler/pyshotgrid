"""
This module collects all default pyshotgrid custom entities.
"""

import fnmatch
from typing import Any, Optional, Union

from .core import Field, SGEntity, new_entity


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

    @property
    def name(self) -> Field:
        """
        :return: The field that represents the name of the Project.
        """
        return self["name"]

    def shots(self, glob_pattern: Optional[str] = None) -> list[SGEntity]:
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

    def assets(self, glob_pattern: Optional[str] = None) -> list[SGEntity]:
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
        pub_types: Optional[Union[str, list[str]]] = None,
        latest: bool = False,
    ) -> list[SGEntity]:
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

    def people(self, only_active: bool = True) -> list[SGEntity]:
        """
        :param only_active: Whether to list only active people or all the people.
        :return: All HumanUsers assigned to this project.
        """
        sg_filter = [["projects", "is", self.to_dict()]]
        if only_active:
            sg_filter.append(["sg_status_list", "is", "act"])

        return [new_entity(self._sg, sg_user) for sg_user in self._sg.find("HumanUser", sg_filter)]

    def playlists(self) -> list[SGEntity]:
        """
        :return: All playlists attached to this project.
        """
        return [
            new_entity(self._sg, sg_playlist)
            for sg_playlist in self._sg.find("Playlist", [["project", "is", self.to_dict()]])
        ]

    def versions(
        self,
        user: Optional[Union[dict[str, Any], SGEntity]] = None,
        pipeline_step: Optional[Union[str, dict[str, Any], SGEntity]] = None,
        latest: bool = False,
    ) -> list[SGEntity]:
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

    @property
    def name(self) -> Field:
        """
        :return: The field that represents the name of the Shot.
        """
        return self["code"]

    def publishes(
        self,
        pub_types: Optional[Union[str, list[str]]] = None,
        latest: bool = False,
    ) -> list[SGEntity]:
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
        names: Optional[list[str]] = None,
        assignee: Optional[Union[dict[str, Any], SGEntity]] = None,
        pipeline_step: Optional[Union[str, dict[str, Any], SGEntity]] = None,
    ) -> list[SGEntity]:
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
        user: Optional[Union[dict[str, Any], SGEntity]] = None,
        pipeline_step: Optional[Union[str, dict[str, Any], SGEntity]] = None,
        latest: bool = False,
    ) -> list[SGEntity]:
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

    @property
    def name(self) -> Field:
        """
        :return: The field that represents the name of the Asset.
        """
        return self["code"]

    def publishes(
        self,
        pub_types: Optional[Union[str, list[str]]] = None,
        latest: bool = False,
    ) -> list[SGEntity]:
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
        names: Optional[list[str]] = None,
        assignee: Optional[Union[dict[str, Any], SGEntity]] = None,
        pipeline_step: Optional[Union[str, dict[str, Any], SGEntity]] = None,
    ) -> list[SGEntity]:
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
        user: Optional[Union[dict[str, Any], SGEntity]] = None,
        pipeline_step: Optional[Union[str, dict[str, Any], SGEntity]] = None,
        latest: bool = False,
    ) -> list[SGEntity]:
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
    def name(self) -> Field:
        """
        :return: The field that represents the name of the Task.
        """
        return self["content"]

    def publishes(
        self,
        pub_types: Optional[Union[str, list[str]]] = None,
        latest: bool = False,
    ) -> list[SGEntity]:
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
        user: Optional[Union[dict[str, Any], SGEntity]] = None,
        pipeline_step: Optional[Union[str, dict[str, Any], SGEntity]] = None,
        latest: bool = False,
    ) -> list[SGEntity]:
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

    @property
    def name(self) -> Field:
        """
        :return: The field that represents the name of the PublishedFile.
        """
        return self["code"]

    def is_latest(self) -> bool:
        """
        :return: Whether this published file is the latest of its kind.
        """
        return self.get_latest() == self

    def get_latest(self) -> SGEntity:
        """
        :return: The latest published file of its kind (which might be this same entity).
        """
        return self.get_all_publishes()[-1]

    def get_next_publishes(self) -> list[SGEntity]:
        """
        :return: The next publishes after this publish.
        """
        all_publishes = self.get_all_publishes()
        index = all_publishes.index(self)
        return all_publishes[index + 1 :]

    def get_previous_publishes(self) -> list[SGEntity]:
        """
        :return: The previous publishes before this publish.
        """
        all_publishes = self.get_all_publishes()
        index = all_publishes.index(self)
        return all_publishes[:index]

    def get_all_publishes(self) -> list[SGEntity]:
        """
        :return: A list of all the published file versions from lowest to highest version number.
        """
        this_publish = self.get(["entity", "published_file_type", "name"], raw_values=True)
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

    @property
    def name(self) -> Field:
        """
        :return: The field that represents the name of the Version.
        """
        return self["code"]

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
    def name(self) -> Field:
        """
        :return: The field that represents the name of the Playlist.
        """
        return self["code"]

    @property
    def media_url(self) -> str:
        """
        :return: The Media center URL for this playlist.
        :raises:
            :RuntimeError: When this playlist is not attached to a project.
        """
        sg_project = self["project"].get()
        if sg_project is None:
            raise RuntimeError(
                f'Cannot get media URL for playlist "{self.id}", '
                f"because it is not attached to a project."
            )
        # Example URL:
        # https://example.shotgunstudio.com/page/media_center?type=Playlist&id=123&project_id=456
        return (
            f"{self.sg.base_url}/page/media_center?type={self._type}&id={self._id}"
            f"&project_id={sg_project['id'].get()}"
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

    @property
    def name(self) -> Field:
        """
        :return: The field that represents the name of the HumanUser.
        """
        return self["name"]

    def versions(
        self,
        entity: Optional[Union[dict[str, Any], SGEntity]] = None,
        pipeline_step: Optional[Union[str, dict[str, Any], SGEntity]] = None,
        latest: bool = False,
    ) -> list[SGEntity]:
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
        names: Optional[list[str]] = None,
        entity: Optional[Union[dict[str, Any], SGEntity]] = None,
        pipeline_step: Optional[Union[str, dict[str, Any], SGEntity]] = None,
    ) -> list[SGEntity]:
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
        pub_types: Optional[Union[str, list[str]]] = None,
        latest: bool = False,
    ) -> list[SGEntity]:
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
