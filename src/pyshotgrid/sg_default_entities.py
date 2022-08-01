"""
This module collects all default pyshotgrid custom entities.

TODO
- Playlist entity
- version entity
- sequence entity
- asset entity
"""
import fnmatch

from .core import convert
from .sg_entity import SGEntity


class SGProject(SGEntity):
    """
    An instance of this class represents a single Project entity in ShotGrid.

    :ivar shotgun_api3.Shotgun sg: A fully initialized instance of shotgun_api3.Shotgun.
    :ivar int project_id: The ID of the project entity.
    """

    def __init__(self, sg, project_id):
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
            return [convert(self._sg, sg_shot)
                    for sg_shot in sg_shots
                    if fnmatch.fnmatchcase(sg_shot['code'], glob_pattern)]
        else:
            return [convert(self._sg, sg_shot) for sg_shot in sg_shots]

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

        return [convert(self._sg, sg_user)
                for sg_user in self._sg.find('HumanUser', sg_filter)]


class SGShot(SGEntity):
    """
    An instance of this class represents a single Shot entity in ShotGrid.

    :ivar shotgun_api3.Shotgun sg: A fully initialized instance of shotgun_api3.Shotgun.
    :ivar int shot_id: The ID of the shot entity.
    """

    def __init__(self, sg, shot_id):
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

        return [convert(self._sg, sg_task)
                for sg_task in self._sg.find('Task', sg_filter)]


class SGTask(SGEntity):
    """
    An instance of this class represents a single Task entity in ShotGrid.

    :ivar shotgun_api3.Shotgun sg: A fully initialized instance of shotgun_api3.Shotgun.
    :ivar int task_id: The ID of the Task entity.
    """

    def __init__(self, sg, task_id):
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

    :ivar shotgun_api3.Shotgun sg: A fully initialized instance of shotgun_api3.Shotgun.
    :ivar int published_file_id: The ID of the PublishedFile entity.
    """

    def __init__(self, sg, published_file_id):
        super(SGPublishedFile, self).__init__(sg, entity_type='PublishedFile',
                                              entity_id=published_file_id)

    # TODO is_latest
    # TODO get_first_publish
    # TODO get_previous_publishes
    # TODO get_next_publishes
    # TODO get_latest_publish
    # TODO get_all_publish_versions


class SGHumanUser(SGEntity):
    """
    An instance of this class represents a single HumanUser entity in ShotGrid.

    :ivar shotgun_api3.Shotgun sg: A fully initialized instance of shotgun_api3.Shotgun.
    :ivar int human_user_id: The ID of the PublishedFile entity.
    """

    def __init__(self, sg, human_user_id):
        super(SGHumanUser, self).__init__(sg,
                                          entity_type='HumanUser',
                                          entity_id=human_user_id)
    # TODO tasks
    # TODO publishes
    # TODO projects
    # TODO versions
    # TODO time logs ?
