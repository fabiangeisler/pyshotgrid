import fnmatch

import shotgun_api3

from .core import convert
from .sg_base_entity import ShotGridEntity


class SGSite(object):
    """
    An instance of this class represents the ShotGrid site as a whole.

    :ivar shotgun_api3.Shotgun sg: A fully initialized instance of shotgun_api3.Shotgun.
    """

    @classmethod
    def from_credentials(cls, base_url, script_name, api_key):
        """
        Initialize the site with some basic ShotGrid API credentials.

        :param str base_url: The URL to the ShotGrid site.
        :param str script_name: The name of the script.
        :param str api_key: The API key.
        :return: An instance of this class.
        :rtype: SGSite
        """
        return cls(sg=shotgun_api3.Shotgun(base_url=base_url,
                                           script_name=script_name,
                                           api_key=api_key))

    def __init__(self, sg):
        self.sg = sg

    def project(self, name_or_id):
        """
        :param int|str name_or_id: The name or id of the project to return.
                                   The name can either match the "tank_name" (recommended)
                                   or the "name" field.
        :return: The found SG project or None.
        :rtype: SGProject|None
        """
        sg_projects = self.projects(names_or_ids=[name_or_id], include_archived=True)
        if sg_projects:
            return sg_projects[0]

    def projects(self, names_or_ids=None, include_archived=False, template_projects=False):
        """
        :param list[int|str]|None names_or_ids: List of names or ids of the projects to return. The
                                                names can either match the "tank_name" (recommended)
                                                or the "name" field.
        :param bool include_archived: Whether to include archived projects or not.
        :param bool template_projects: Whether to return template projects or not.
        :return: A list of SG projects.
        :rtype: list[SGProject]
        """
        sg_projects = self.sg.find('Project',
                                   [['is_template', 'is', template_projects]],
                                   ['tank_name', 'name'],
                                   include_archived_projects=include_archived)

        if names_or_ids is not None:
            if isinstance(names_or_ids[0], int):
                sg_projects = [sg_project
                               for sg_project in sg_projects
                               if sg_project['id'] in names_or_ids]
            else:
                sg_projects = [sg_project
                               for sg_project in sg_projects
                               if (sg_project['tank_name'] in names_or_ids or
                                   sg_project['name'] in names_or_ids)]

        return [convert(self.sg, sg_project) for sg_project in sg_projects]


class SGProject(ShotGridEntity):
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
                                      "TEST_01_*" would return all shots that start with "TEST_01_".
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


class SGShot(ShotGridEntity):
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


class SGPublishedFile(ShotGridEntity):
    """
    An instance of this class represents a single PublishedFile entity in ShotGrid.

    :ivar shotgun_api3.Shotgun sg: A fully initialized instance of shotgun_api3.Shotgun.
    :ivar int published_file_id: The ID of the PublishedFile entity.
    """

    def __init__(self, sg, published_file_id):
        super(SGPublishedFile, self).__init__(sg, entity_type='PublishedFile',
                                              entity_id=published_file_id)
