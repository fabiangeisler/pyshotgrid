import typing
from typing import Any, Dict, List, Optional, Type, Union  # noqa: F401

if typing.TYPE_CHECKING:
    import shotgun_api3  # noqa: F401

    from .sg_entity import SGEntity  # noqa: F401

from .core import convert_fields_to_dicts, convert_filters_to_dict, new_entity
from .field import FieldSchema


class SGSite(object):
    """
    An instance of this class represents a ShotGrid site as a whole.

    .. Note::

        Try to avoid creating instances of this class in production code and
        use the :py:meth:`pyshotgrid.new_site <pyshotgrid.core.new_site>`
        method instead. This gives you more ways to initialize the this class
        and ensures that the plugin system is correctly used.
    """

    def __init__(self, sg):
        # type: (shotgun_api3.shotgun.Shotgun) -> None
        """
        :param sg: A fully initialized instance of shotgun_api3.Shotgun.
        """
        self._sg = sg

    @property
    def sg(self):
        # type: () -> shotgun_api3.shotgun.Shotgun
        """
        :return: The Shotgun instance that the entity belongs to.
        """
        return self._sg

    def create(self, entity_type, data):
        # type: (str,Dict[str,Any]) -> Optional[Type[SGEntity]]
        """
        The same function as
        :py:meth:`Shotgun.create <shotgun_api3:shotgun_api3.shotgun.Shotgun.create>`,
        but it accepts and returns a pyshotgrid object.

        :param entity_type: The type of the entity to create.
        :param data: dict of fields and values to set on creation.
                     The values can contain pysg objects.
        :return: The new created entity.
        """
        # noinspection PyTypeChecker
        return new_entity(
            self._sg,
            self._sg.create(
                entity_type=entity_type,
                data=convert_fields_to_dicts(data),
                return_fields=None,
            ),
        )

    def find(
        self,
        entity_type,  # type: str
        filters,  # type: List[List[Any]]
        order=None,  # type: Optional[Dict[str,str]]
        filter_operator=None,  # type: Optional[str]
        limit=0,  # type: int
        retired_only=False,  # type: bool
        page=0,  # type: int
        include_archived_projects=True,  # type: bool
        additional_filter_presets=None,  # type: Optional[str]
    ):
        # type: (...) -> List[Optional[Type[SGEntity]]]
        """
        The same function as
        :py:meth:`Shotgun.find <shotgun_api3:shotgun_api3.shotgun.Shotgun.find>`, but it
        accepts and returns pyshotgrid objects.

        :param entity_type:
        :param filters:
        :param order:
        :param filter_operator:
        :param limit:
        :param retired_only:
        :param page:
        :param include_archived_projects:
        :param additional_filter_presets:
        :return:
        """
        # noinspection PyTypeChecker
        return [
            new_entity(self._sg, sg_entity)
            for sg_entity in self._sg.find(
                entity_type=entity_type,
                filters=convert_filters_to_dict(filters),
                fields=None,
                order=order,
                filter_operator=filter_operator,
                limit=limit,
                retired_only=retired_only,
                page=page,
                include_archived_projects=include_archived_projects,
                additional_filter_presets=additional_filter_presets,
            )
        ]

    def find_one(
        self,
        entity_type,  # type: str
        filters,  # type: List[List[Any]]
        order=None,  # type: Optional[Dict[str,str]]
        filter_operator=None,  # type: Optional[str]
        limit=0,  # type: int
        retired_only=False,  # type: bool
        page=0,  # type: int
        include_archived_projects=True,  # type: bool
        additional_filter_presets=None,  # type: Optional[str]
    ):
        # type: (...) -> Optional[Type[SGEntity]]
        """
        The same function as
        :py:meth:`Shotgun.find_one <shotgun_api3:shotgun_api3.shotgun.Shotgun.find_one>` ,
        but it accepts and returns pyshotgrid objects.
        """
        # TODO allow entering the display name for the entity_type
        result = self.find(
            entity_type=entity_type,
            filters=filters,
            order=order,
            filter_operator=filter_operator,
            limit=limit,
            retired_only=retired_only,
            page=page,
            include_archived_projects=include_archived_projects,
            additional_filter_presets=additional_filter_presets,
        )
        if result:
            return result[0]
        return None

    def entity_field_schemas(self):
        # type: () -> Dict[str,Dict[str,FieldSchema]]
        """
        :return: The field schemas for all entities of the current ShotGrid Site.
        """
        result = {}
        for entity, field_schemas in self._sg.schema_read().items():
            result[entity] = {
                field_name: FieldSchema(self._sg, entity, field_name)
                for field_name in field_schemas.keys()
            }
        return result

    def project(self, name_or_id):
        # type: (Union[str,int]) -> Optional[Type[SGEntity]]
        """
        :param name_or_id: The name or id of the project to return.
                           The name can either match the "tank_name" (recommended)
                           or the "name" field.
        :return: The found SG project or None.
        """
        sg_projects = self.projects(names_or_ids=[name_or_id], include_archived=True)
        if sg_projects:
            return sg_projects[0]
        return None

    def projects(
        self, names_or_ids=None, include_archived=False, template_projects=False
    ):
        # type: (Optional[List[Union[str,int]]],bool,bool) -> List[Type[SGEntity]]
        """
        :param names_or_ids: List of names or ids of the projects to return. The
                             names can either match the "tank_name" (recommended)
                             or the "name" field.
        :param include_archived: Whether to include archived projects or not.
        :param template_projects: Whether to return template projects or not.
        :return: A list of SG projects.
        """
        sg_projects = self._sg.find(
            "Project",
            [["is_template", "is", template_projects]],
            ["tank_name", "name"],
            include_archived_projects=include_archived,
        )

        if names_or_ids is not None:
            if isinstance(names_or_ids[0], int):
                sg_projects = [
                    sg_project
                    for sg_project in sg_projects
                    if sg_project["id"] in names_or_ids
                ]
            else:
                sg_projects = [
                    sg_project
                    for sg_project in sg_projects
                    if (
                        sg_project["tank_name"] in names_or_ids
                        or sg_project["name"] in names_or_ids
                    )
                ]

        return [new_entity(self._sg, sg_project) for sg_project in sg_projects]

    def pipeline_configuration(
        self,
        name_or_id=None,  # type: Optional[Union[str,int]]
        project=None,  # type: Optional[Union[Dict[str,Any],Type[SGEntity]]]
    ):
        # type: (...) -> Optional[Type[SGEntity]]
        """
        :param name_or_id: Name or ID of the PipelineConfiguration.
        :param project: The project that the PipelineConfiguration is attached to.
        :return: The PipelineConfiguration.
        """
        base_filter = []
        if name_or_id is not None:
            if isinstance(name_or_id, int):
                return new_entity(
                    self._sg, entity_type="PipelineConfiguration", entity_id=name_or_id
                )
            else:
                base_filter = [["code", "is", name_or_id]]

        if project is not None:
            if isinstance(project, dict):
                base_filter.append(["project", "is", project])
            else:
                base_filter.append(["project", "is", project.to_dict()])

        sg_pipe_config = self._sg.find_one("PipelineConfiguration", base_filter)

        if sg_pipe_config:
            return new_entity(self._sg, sg_pipe_config)
        return None

    def people(self, additional_sg_filter=None):
        # type: (Optional[List[Dict[str,Any]]]) -> List[Optional[Type[SGEntity]]]
        """
        :param additional_sg_filter:
        :return: All HumanUsers of this ShotGrid site.
        """
        # TODO add "only_active" and "name_or_id" parameter
        return [
            new_entity(self._sg, sg_user)
            for sg_user in self._sg.find("HumanUser", additional_sg_filter or [])
        ]
