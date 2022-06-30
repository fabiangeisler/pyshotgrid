import shotgun_api3

from .core import convert


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
        self._sg = sg

    @property
    def sg(self):
        """
        :return: The Shotgun instance that the entity belongs to.
        :rtype: shotgun_api3.Shotgun
        """
        return self._sg

    def create(self, entity_type, data):
        """
        The same function as shotgun_api3.Shotgun.create,
        but it accepts and returns a pyshotgrid object.
        """
        # TODO convert data input pysg objects
        return convert(self._sg, self._sg.create(entity_type=entity_type,
                                                 data=data,
                                                 return_fields=None))

    def find(self, entity_type, filters, fields=None, order=None, filter_operator=None, limit=0,
             retired_only=False, page=0, include_archived_projects=True,
             additional_filter_presets=None):
        """
        The same function as shotgun_api3.Shotgun.find,
        but it accepts and returns pyshotgrid objects.

        :param entity_type:
        :param filters:
        :param fields:
        :param order:
        :param filter_operator:
        :param limit:
        :param retired_only:
        :param page:
        :param include_archived_projects:
        :param additional_filter_presets:
        :return:
        """
        # TODO convert filter entities
        return [convert(self._sg, sg_entity)
                for sg_entity in self._sg.find(
                entity_type=entity_type,
                filters=filters,
                fields=fields,
                order=order,
                filter_operator=filter_operator,
                limit=limit,
                retired_only=retired_only,
                page=page,
                include_archived_projects=include_archived_projects,
                additional_filter_presets=additional_filter_presets)]

    def find_one(self, entity_type, filters, fields=None, order=None, filter_operator=None, limit=0,
                 retired_only=False, page=0, include_archived_projects=True,
                 additional_filter_presets=None):
        """
        The same function as shotgun_api3.Shotgun.find_one,
        but it accepts and returns pyshotgrid objects.

        """
        # TODO allow entering the display name for the entity_type
        result = self.find(entity_type=entity_type,
                           filters=filters,
                           fields=fields,
                           order=order,
                           filter_operator=filter_operator,
                           limit=limit,
                           retired_only=retired_only,
                           page=page,
                           include_archived_projects=include_archived_projects,
                           additional_filter_presets=additional_filter_presets)[0]
        if result:
            return result[0]

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
        sg_projects = self._sg.find('Project',
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

        return [convert(self._sg, sg_project) for sg_project in sg_projects]

    def pipeline_configuration(self, name_or_id=None, project=None):
        """
        :param int|str|None name_or_id: Name or ID of the PipelineConfiguration.
        :param dict|ShotGridEntity|None project: The project that the PipelineConfiguration
                                                 is attached to.
        :return: The PipelineConfiguration.
        :rtype: ShotGridEntity|None
        """
        base_filter = []
        if name_or_id is not None:
            if isinstance(name_or_id, int):
                base_filter = [['id', 'is', name_or_id]]
            else:
                base_filter = [['code', 'is', name_or_id]]

        if project is not None:
            if isinstance(project, dict):
                base_filter.append(['project', 'in', project])
            else:
                base_filter.append(['project', 'in', project.to_dict()])

        sg_pipe_config = self._sg.find_one('PipelineConfiguration',
                                           base_filter)

        if sg_pipe_config:
            return convert(self._sg, sg_pipe_config)

    def people(self, additional_sg_filter=None):
        """
        :param list|None additional_sg_filter:
        :return: All HumanUsers of this ShotGrid site.
        :rtype: list[SGHumanUser]
        """
        return [convert(self._sg, sg_user)
                for sg_user in self._sg.find('HumanUser', additional_sg_filter or [])]
