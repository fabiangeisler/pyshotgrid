"""
This module collects all default pyshotgrid custom entities.
"""
import fnmatch

from .core import new_entity
from .sg_entity import SGEntity


class SGProject(SGEntity):
    """
    An instance of this class represents a single Project entity in ShotGrid.
    """

    def __init__(self, sg, project_id):
        """
        :param shotgun_api3.shotgun.Shotgun sg:
            A fully initialized instance of shotgun_api3.Shotgun.
        :param int project_id: The ID of the project entity.
        """
        super(SGProject, self).__init__(sg, entity_type='Project', entity_id=project_id)

    def shots(self, glob_pattern=None):
        """
        :param str|None glob_pattern: A glob to match the shots to return. For example
                                      `TEST_01_*` would return all shots that start with `TEST_01_`.
        :return: All the shots from this project.
        :rtype: list[SGShot]
        """
        sg_shots = self.sg.find('Shot', [['project', 'is', self.to_dict()]], ['code'])
        if glob_pattern is not None:
            return [new_entity(self._sg, sg_shot)
                    for sg_shot in sg_shots
                    if fnmatch.fnmatchcase(sg_shot['code'], glob_pattern)]
        else:
            return [new_entity(self._sg, sg_shot) for sg_shot in sg_shots]

    def assets(self, glob_pattern=None):
        """
        :param str|None glob_pattern: A glob to match the assets to return. For example
                                      `TEST_*` would return all assets that start with `TEST_`.
        :return: All the assets from this project.
        :rtype: list[SGAsset]
        """
        sg_assets = self.sg.find('Asset', [['project', 'is', self.to_dict()]], ['code'])
        if glob_pattern is not None:
            return [new_entity(self._sg, sg_asset)
                    for sg_asset in sg_assets
                    if fnmatch.fnmatchcase(sg_asset['code'], glob_pattern)]
        else:
            return [new_entity(self._sg, sg_shot) for sg_shot in sg_assets]

    def publishes(self, pub_types=None, latest=False, additional_sg_filter=None):
        """
        :param str|list[str]|None pub_types: The names of the Publish File Types to return.
        :param bool latest: Whether to get the "latest" publishes or not. This uses the
          same logic as the tk-multi-loader2 app which is as follows:

            - group all publishes with the same "name" field together
            - from these get the publishes with the highest "version_number" field
            - if there are publishes with the same "name" and "version_number" the
              newest one wins.
        :param additional_sg_filter:
        :return: All published files from this project.
        :rtype: list[SGPublishedFile]
        """
        return self._publishes(base_filter=[['project', 'is', self.to_dict()]],
                               pub_types=pub_types,
                               latest=latest,
                               additional_sg_filter=additional_sg_filter)

    def people(self, additional_sg_filter=None):
        """
        :param list|None additional_sg_filter:
        :return: All HumanUsers assigned to this project.
        :rtype: list[SGHumanUser]
        """
        sg_filter = [['projects', 'contains', self.to_dict()]]
        if additional_sg_filter is not None:
            sg_filter += additional_sg_filter

        return [new_entity(self._sg, sg_user)
                for sg_user in self._sg.find('HumanUser', sg_filter)]

    def playlists(self):
        """
        :return: All playlists attached to this project.
        :rtype: list[SGPlaylist]
        """
        return [new_entity(self._sg, sg_playlist)
                for sg_playlist in self._sg.find('Playlist', [['project', 'is', self.to_dict()]])]


class SGShot(SGEntity):
    """
    An instance of this class represents a single Shot entity in ShotGrid.
    """

    def __init__(self, sg, shot_id):
        """
        :param shotgun_api3.shotgun.Shotgun sg:
            A fully initialized instance of shotgun_api3.Shotgun.
        :param int shot_id: The ID of the shot entity.
        """
        super(SGShot, self).__init__(sg, entity_type='Shot', entity_id=shot_id)

    def publishes(self, pub_types=None, latest=False, additional_sg_filter=None):
        """
        :param str|list[str]|None pub_types: The names of the Publish File Types to return.
        :param bool latest: Whether to get the "latest" publishes or not. This uses the
                            same logic as the tk-multi-loader2 app which is as follows:

                              - group all publishes with the same "name" field together
                              - from these get the publishes with the highest "version_number" field
                              - if there are publishes with the same "name" and "version_number" the
                                newest one wins.
        :param additional_sg_filter:
        :return: All published files from this shot.
        :rtype: list[SGPublishedFile]
        """
        return self._publishes(base_filter=[['entity', 'is', self.to_dict()]],
                               pub_types=pub_types,
                               latest=latest,
                               additional_sg_filter=additional_sg_filter)

    def tasks(self, names=None, pipeline_step=None):
        """
        :param list[str]|None names: The names of Tasks to return.
        :param str|dict|SGEntity|None pipeline_step: Name, short name or entity object
                                                     or the Pipeline Step to filter by.
        :returns: A list of Tasks
        :rtype: list[SGTask]
        """
        sg_filter = [['entity', 'is', self.to_dict()]]

        if names is not None:
            if len(names) == 1:
                names_filter = ['code', 'is', names[0]]
            else:
                names_filter = {"filter_operator": "any", "filters": []}
                for name in names:
                    names_filter['filters'].append(
                        ['code', 'is', name])
            sg_filter.append(names_filter)

        if pipeline_step is not None:
            if isinstance(pipeline_step, dict):
                sg_filter.append(['step', 'is', pipeline_step])
            elif isinstance(pipeline_step, SGEntity):
                sg_filter.append(['step', 'is', pipeline_step.to_dict()])
            else:
                sg_filter.append({"filter_operator": "any",
                                  "filters": [['step.Step.code', 'is', pipeline_step],
                                              ['step.Step.short_name', 'is', pipeline_step]]})

        return [new_entity(self._sg, sg_task)
                for sg_task in self._sg.find('Task', sg_filter)]


class SGAsset(SGEntity):
    """
    An instance of this class represents a single Asset entity in ShotGrid.
    """

    def __init__(self, sg, asset_id):
        """
        :param shotgun_api3.shotgun.Shotgun sg:
            A fully initialized instance of shotgun_api3.Shotgun.
        :param int asset_id: The ID of the Asset entity.
        """
        super(SGAsset, self).__init__(sg, entity_type='Shot', entity_id=asset_id)

    def publishes(self, pub_types=None, latest=False, additional_sg_filter=None):
        """
        :param str|list[str]|None pub_types: The names of the Publish File Types to return.
        :param bool latest: Whether to get the "latest" publishes or not. This uses the
                            same logic as the tk-multi-loader2 app which is as follows:

                              - group all publishes with the same "name" field together
                              - from these get the publishes with the highest "version_number" field
                              - if there are publishes with the same "name" and "version_number" the
                                newest one wins.
        :param additional_sg_filter:
        :return: All published files from this asset.
        :rtype: list[SGPublishedFile]
        """
        return self._publishes(base_filter=[['entity', 'is', self.to_dict()]],
                               pub_types=pub_types,
                               latest=latest,
                               additional_sg_filter=additional_sg_filter)

    def tasks(self, names=None, pipeline_step=None):
        """
        :param list[str]|None names: The names of Tasks to return.
        :param str|dict|SGEntity|None pipeline_step: Name, short name or entity object
                                                     or the Pipeline Step to filter by.
        :returns: A list of Tasks
        :rtype: list[SGTask]
        """
        sg_filter = [['entity', 'is', self.to_dict()]]

        if names is not None:
            if len(names) == 1:
                names_filter = ['code', 'is', names[0]]
            else:
                names_filter = {"filter_operator": "any", "filters": []}
                for name in names:
                    names_filter['filters'].append(
                        ['code', 'is', name])
            sg_filter.append(names_filter)

        if pipeline_step is not None:
            if isinstance(pipeline_step, dict):
                sg_filter.append(['step', 'is', pipeline_step])
            elif isinstance(pipeline_step, SGEntity):
                sg_filter.append(['step', 'is', pipeline_step.to_dict()])
            else:
                sg_filter.append({"filter_operator": "any",
                                  "filters": [['step.Step.code', 'is', pipeline_step],
                                              ['step.Step.short_name', 'is', pipeline_step]]})

        return [new_entity(self._sg, sg_task)
                for sg_task in self._sg.find('Task', sg_filter)]


class SGTask(SGEntity):
    """
    An instance of this class represents a single Task entity in ShotGrid.
    """

    def __init__(self, sg, task_id):
        """
        :param shotgun_api3.shotgun.Shotgun sg:
            A fully initialized instance of shotgun_api3.Shotgun.
        :param int task_id: The ID of the Task entity.
        """
        super(SGTask, self).__init__(sg, entity_type='Task', entity_id=task_id)

    def publishes(self, pub_types=None, latest=False, additional_sg_filter=None):
        """
        :param str|list[str]|None pub_types: The names of the Publish File Types to return.
        :param bool latest: Whether to get the "latest" publishes or not. This uses the
                            same logic as the tk-multi-loader2 app which is as follows:

                             - group all publishes with the same "name" field together
                             - from these get the publishes with the highest "version_number" field
                             - if there are publishes with the same "name" and "version_number" the
                               newest one wins.
        :param additional_sg_filter:
        :return: All published files from this shot.
        :rtype: list[SGPublishedFile]
        """
        return self._publishes(base_filter=[['task', 'is', self.to_dict()]],
                               pub_types=pub_types,
                               latest=latest,
                               additional_sg_filter=additional_sg_filter)


class SGPublishedFile(SGEntity):
    """
    An instance of this class represents a single PublishedFile entity in ShotGrid.
    """

    def __init__(self, sg, published_file_id):
        """
        :param shotgun_api3.shotgun.Shotgun sg:
            A fully initialized instance of shotgun_api3.Shotgun.
        :param int published_file_id: The ID of the PublishedFile entity.
        """
        super(SGPublishedFile, self).__init__(sg, entity_type='PublishedFile',
                                              entity_id=published_file_id)

    # TODO is_latest
    # TODO get_first_publish
    # TODO get_previous_publishes
    # TODO get_next_publishes
    # TODO get_latest_publish
    # TODO get_all_publish_versions


class SGVersion(SGEntity):
    """
    An instance of this class represents a single Version entity in ShotGrid.
    """

    def __init__(self, sg, version_id):
        """
        :param shotgun_api3.shotgun.Shotgun sg:
            A fully initialized instance of shotgun_api3.Shotgun.
        :param int version_id: The ID of the Version entity.
        """
        super(SGVersion, self).__init__(sg, entity_type='Version', entity_id=version_id)


class SGPlaylist(SGEntity):
    """
    An instance of this class represents a single Playlist entity in ShotGrid.
    """

    def __init__(self, sg, playlist_id):
        """
        :param shotgun_api3.shotgun.Shotgun sg:
            A fully initialized instance of shotgun_api3.Shotgun.
        :param int playlist_id: The ID of the Playlist entity.
        """
        super(SGPlaylist, self).__init__(sg, entity_type='Playlist', entity_id=playlist_id)

    @property
    def media_url(self):
        """
        :return: The Media center URL for this playlist.
        :rtype: str
        :raises:
            :RuntimeError: When this playlist is not attached to a project.
        """
        sg_project = self['project'].get()
        if sg_project is None:
            raise RuntimeError('Cannot get media URL for playlist "{}"'
                               ', because it is not attached to a project.'.format(self.id))
        # Example URL:
        # https://example.shotgunstudio.com/page/media_center?type=Playlist&id=123&project_id=456
        return ('{}/page/media_center?type={}&id={}&project_id={}'
                '').format(self.sg.base_url, self._type, self._id, sg_project['id'].get())


class SGHumanUser(SGEntity):
    """
    An instance of this class represents a single HumanUser entity in ShotGrid.
    """

    def __init__(self, sg, human_user_id):
        """
        :param shotgun_api3.shotgun.Shotgun sg:
            A fully initialized instance of shotgun_api3.Shotgun.
        :param int human_user_id: The ID of the PublishedFile entity.
        """
        super(SGHumanUser, self).__init__(sg,
                                          entity_type='HumanUser',
                                          entity_id=human_user_id)

    def tasks(self, names=None, project=None, pipeline_step=None):
        """
        :param list[str]|None names: The names of Tasks to return.
        :param str|dict|SGEntity|None project: Name, tank_name or entity object
                                               or the Project to filter by.
        :param str|dict|SGEntity|None pipeline_step: Name, short name or entity object
                                                     or the Pipeline Step to filter by.
        :returns: A list of Tasks
        :rtype: list[SGTask]
        """
        sg_filter = [{"filter_operator": "any",
                      "filters": [
                          ['task_assignees', 'contains', self.to_dict()],
                          ['task_assignees.Group.users', 'contains', self.to_dict()],
                      ]}]

        if names is not None:
            if len(names) == 1:
                names_filter = ['code', 'is', names[0]]
            else:
                names_filter = {"filter_operator": "any", "filters": []}
                for name in names:
                    names_filter['filters'].append(
                        ['code', 'is', name])
            sg_filter.append(names_filter)

        if project is not None:
            if isinstance(project, dict):
                sg_filter.append(['project', 'is', project])
            elif isinstance(project, SGEntity):
                sg_filter.append(['project', 'is', project.to_dict()])
            else:
                sg_filter.append({"filter_operator": "any",
                                  "filters": [['project.Project.code', 'is', project],
                                              ['project.Project.tank_name', 'is', project]]})

        if pipeline_step is not None:
            if isinstance(pipeline_step, dict):
                sg_filter.append(['step', 'is', pipeline_step])
            elif isinstance(pipeline_step, SGEntity):
                sg_filter.append(['step', 'is', pipeline_step.to_dict()])
            else:
                sg_filter.append({"filter_operator": "any",
                                  "filters": [['step.Step.code', 'is', pipeline_step],
                                              ['step.Step.short_name', 'is', pipeline_step]]})

        return [new_entity(self._sg, sg_task)
                for sg_task in self._sg.find('Task', sg_filter)]

    def publishes(self, pub_types=None, latest=False, additional_sg_filter=None):
        """
        :param str|list[str]|None pub_types: The names of the Publish File Types to return.
        :param bool latest: Whether to get the "latest" publishes or not. This uses the
                            same logic as the tk-multi-loader2 app which is as follows:

                             - group all publishes with the same "name" field together
                             - from these get the publishes with the highest "version_number" field
                             - if there are publishes with the same "name" and "version_number" the
                               newest one wins.
        :param additional_sg_filter:
        :return: All published files from this shot.
        :rtype: list[SGPublishedFile]
        """
        return self._publishes(base_filter=[['created_by', 'is', self.to_dict()]],
                               pub_types=pub_types,
                               latest=latest,
                               additional_sg_filter=additional_sg_filter)
