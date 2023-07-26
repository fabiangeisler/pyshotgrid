import os
from typing import Any, Dict, List, Optional, Type, Union  # noqa: F401

import shotgun_api3
import shotgun_api3.lib.mockgun


class SGEntity(object):
    """
    An instance of this class represents a single entity in ShotGrid.

    .. Note::

        Try to avoid creating instances of this class in production code and
        use the :py:meth:`pyshotgrid.new_entity <pyshotgrid.core.new_entity>`
        method instead. This will make sure that you always get the correct
        entity class to work with.
    """

    #: The SG entity type that will be used when you do not specify it in the
    #: init arguments. For the base SGEntity this should always be None, but
    #: for sub classes this should be set to the SG entity type that the
    #: class should represent.
    DEFAULT_SG_ENTITY_TYPE = None  # type: Optional[str]

    def __init__(self, sg, entity_id, entity_type=None):
        # type: (shotgun_api3.shotgun.Shotgun, int, Optional[str]) -> None
        """
        :param sg: A fully initialized instance of shotgun_api3.Shotgun.
        :param entity_id: The ID of the ShotGrid entity.
        :param entity_type: The ShotGrid type of the entity.
        """
        self._sg = sg
        self._id = entity_id
        if entity_type is None:
            if self.DEFAULT_SG_ENTITY_TYPE is None:
                raise ValueError(
                    "Cannot construct an instance of {}. "
                    "DEFAULT_SG_ENTITY_TYPE of the class is None and"
                    "no entity_type argument was given."
                    "".format(self.__class__.__name__)
                )
            else:
                entity_type = self.DEFAULT_SG_ENTITY_TYPE
        self._type = entity_type

    def __str__(self):
        # type: () -> str
        return "{} - Type: {} - ID: {} - URL: {}".format(
            self.__class__.__name__, self._type, self._id, self.url
        )

    @property
    def id(self):
        # type: () -> int
        """
        :return: The ID of the ShotGrid entity.
        """
        return self._id

    @property
    def type(self):
        # type: () -> str
        """
        :return: The type of the ShotGrid entity.
        """
        return self._type

    @property
    def sg(self):
        # type: () -> shotgun_api3.shotgun.Shotgun
        """
        :return: The Shotgun instance that the entity belongs to.
        """
        return self._sg

    @property
    def site(self):
        # type: () -> SGSite
        """
        :return: The pyshotgrid site for this entity.
        """
        return new_site(self._sg)

    @property
    def url(self):
        # type: () -> str
        """
        :return: The ShotGrid URL for this entity.

            .. note::

               This will only work on entities that have a detail view enabled
               in the system settings.
        """
        return "{}/detail/{}/{}".format(self.sg.base_url, self._type, self._id)

    @property
    def name(self):
        # type: () -> Field
        """
        :return: The field that represents the name of the entity.
                 Usually either the "code" or "name" field.
        :raises:
            :RuntimeError: When the current entity does not have a "name" or "code" field.
        """
        sg_entity = self._sg.find_one(
            self._type, [["id", "is", self._id]], ["name", "code"]
        )
        if "name" in sg_entity and sg_entity["name"] is not None:
            return self["name"]
        elif "code" in sg_entity and sg_entity["code"] is not None:
            return self["code"]
        else:
            raise RuntimeError(
                "Cannot find a field for the name. "
                '"{}" entities has neither a "name" nor a "code" field.'
                "".format(self._type)
            )

    def __eq__(self, other):
        # type: (Any) -> bool
        """
        Compare SGEntities against each other.
        We consider the entities equal if all these are true:
          - the other instance is a (sub-)class of SGEntity
          - the ID's match
          - the entity types match
          - the base URL of the Shotgun instances is the same.

        :param other: The other python object to compare to.
        :return: Whether the 2 instances represent the same entity in ShotGrid.
        """
        return isinstance(other, SGEntity) and all(
            (
                self._id == other.id,
                self._type == other.type,
                self._sg.base_url == other.sg.base_url,
            )
        )

    def __getitem__(self, field):
        # type: (str) -> Field
        """
        Enabling dict notation to query fields of the entity from ShotGrid.

        :param field: The field to query.
        :return: The value of the field. Any entities will be automatically converted to
                 pyshotgrid objects.
        """
        return Field(name=field, entity=self)

    def fields(self, project_entity=None):
        # type: (Union[Dict[str,Any],SGEntity,None]) -> List[Field]
        """
        :param project_entity: A project entity to filter by.
        :return: All fields from this entity. If a project entity is given
                 only fields that are visible to the project are returned.
        """
        if project_entity is not None and not isinstance(project_entity, dict):
            project_entity = project_entity.to_dict()

        sg_entity_fields = self.sg.schema_field_read(
            self._type, project_entity=project_entity
        )
        fields = [
            field
            for field, schema in sg_entity_fields.items()
            if schema["visible"]["value"]
        ]

        return [Field(name=field, entity=self) for field in fields]

    def all_field_values(self, project_entity=None, raw_values=False):
        # type: (Optional[Union[Dict[str,Any],SGEntity]],bool) -> Dict[str,Any]
        """
        :param project_entity: A project entity to filter by.
        :param raw_values: Whether to convert entities to pysg objects or not.
        :return: All fields and values from this entity in a dict. If a project entity is given
                 only fields that are visible to the project are returned.
        """
        if project_entity is not None and not isinstance(project_entity, dict):
            project_entity = project_entity.to_dict()

        sg_entity_fields = self.sg.schema_field_read(
            self._type, project_entity=project_entity
        )
        fields = [
            field
            for field, schema in sg_entity_fields.items()
            if schema["visible"]["value"]
        ]
        all_fields = self.sg.find_one(self._type, [["id", "is", self._id]], fields)

        if raw_values:
            return all_fields
        else:
            return convert_fields_to_pysg(self._sg, all_fields)

    def to_dict(self):
        # type: () -> Dict[str,Any]
        # noinspection PyUnresolvedReferences
        """
        Creates a dict with just "type" and "id" (and does not call SG).

        Example::

            >>> sg_entity.to_dict()
            {'type': 'CustomEntity01', 'id': 1}

        :returns: The entity as a dict which is ready to consume by the shotgun_api3 methods.
        """
        return {"id": self._id, "type": self._type}

    def batch_update_dict(self, data):
        # type: (Dict[str,Any]) -> Dict[str,Any]
        """
        :param data: A dict with the fields and values to set.
        :returns: A dict that can be used in a shotgun.batch() call to update some fields.
                  Useful when you want to collect field changes and set them in one go.
        """
        return {
            "request_type": "update",
            "entity_type": self._type,
            "entity_id": self._id,
            "data": convert_fields_to_dicts(data),
        }

    def set(self, data, multi_entity_update_modes=None):
        # type: (Dict[str,Any],Optional[Dict[str,Any]]) -> None
        """
        Set many fields at once on this entity.

        :param data: A dict with the fields and values to set.
        :param multi_entity_update_modes: Optional dict indicating what update mode to use
            when updating a multi-entity link field. The keys in the dict are the fields to set
            the mode for, and the values from the dict are one of ``set``, ``add``, or ``remove``.
            Defaults to ``set``.
            ::

                multi_entity_update_modes={"shots": "add", "assets": "remove"}
        """
        self.sg.update(
            self._type,
            self._id,
            data=convert_fields_to_dicts(data),
            multi_entity_update_modes=multi_entity_update_modes,
        )

    def get(self, fields, raw_values=False):
        # type: (List[str],bool) -> Dict[str,Any]
        """
        Query many fields at once on this entity.

        :param fields: A list of fields to query from this entity.
        :param raw_values: Any entities will be converted to pyshotgrid instances.
                                If you set this parameter to True you can turn this behaviour off.
        :return: A dict with the fields and their corresponding values.
        """
        sg_fields = self.sg.find_one(self._type, [["id", "is", self._id]], fields)

        del sg_fields["id"]
        del sg_fields["type"]

        if raw_values:
            return sg_fields
        else:
            return convert_fields_to_pysg(self._sg, sg_fields)

    def delete(self):
        # type: () -> bool
        """
        Delete this entity.

        .. Note::

            The python object that represents this entity does not make sense any more after you
            ran this method and will create errors if you keep calling functions on it.

        :return: Whether the entity was successfully deleted.
        """
        return self._sg.delete(self._type, self._id)

    @property
    def entity_display_name(self):
        # type: () -> str
        """
        :return: The display name of the current entity type.
        """
        return self.schema()["name"]["value"]

    def schema(self):
        # type: () -> Dict[str,Dict[str,Any]]
        """
        :return: The schema for the current entity.
        """
        return self.sg.schema_entity_read()[self._type]

    def field_schemas(self):
        # type: () -> Dict[str,FieldSchema]
        """
        :return: The schemas of all the entity fields.
        """
        return {
            field: FieldSchema(self._sg, self._type, field)
            for field in self.sg.schema_field_read(self._type)
        }

    def _publishes(
        self,
        base_filter=None,  # type: Optional[List[Any]]
        pub_types=None,  # type: Optional[Union[str,List[str]]]
        latest=False,  # type: bool
    ):
        # type: (...) ->  List[SGEntity]
        """
        This function is meant as a base for a "publishes" function on a sub class. Publishes
        are stored in different fields for each entity and not every entity has a published file.
        This is why this function is hidden by default.

        :param base_filter: The basic sg filter to get the publishes that are associated with
                            this entity.
        :param pub_types: The names of the Publish File Types to return.
        :param latest: Whether to get the "latest" publishes or not. This uses the
                       same logic as the tk-multi-loader2 app which is as follows:
                        - group all publishes with the same "name" field together
                        - from these get the publishes with the highest "version_number" field
                        - if there are publishes with the same "name" and "version_number" the
                          newest one wins.
        :return: All published files from this shot.
        """
        result_filter = base_filter or []
        if pub_types is not None:
            if isinstance(pub_types, list):
                pub_types_filter = {
                    "filter_operator": "any",
                    "filters": [
                        ["published_file_type.PublishedFileType.code", "is", pub_type]
                        for pub_type in pub_types
                    ],
                }  # type: Union[Dict[str,Any],List[Any]]
            else:
                pub_types_filter = [
                    "published_file_type.PublishedFileType.code",
                    "is",
                    pub_types,
                ]
            result_filter.append(pub_types_filter)

        sg_publishes = self.sg.find(
            "PublishedFile", result_filter, ["name", "version_number", "created_at"]
        )
        if latest:
            # group publishes by "name"
            tmp = {}  # type: Dict[str,List[Dict[str,Any]]]
            for sg_publish in sg_publishes:
                if sg_publish["name"] in tmp:
                    tmp[sg_publish["name"]].append(sg_publish)
                else:
                    tmp[sg_publish["name"]] = [sg_publish]

            # sort them by date and than by version_number which sorts the latest publish to the
            # last position.
            result = []
            for publishes in tmp.values():
                publishes.sort(
                    key=lambda pub: (pub["created_at"], pub["version_number"])
                )
                result.append(publishes[-1])

            # Sort one more time by name.
            result.sort(key=lambda pub: pub["name"])

            sg_publishes = result

        return [new_entity(self._sg, sg_publish) for sg_publish in sg_publishes]

    def _tasks(
        self,
        names=None,  # type: Optional[List[str]]
        entity=None,  # type: Optional[Union[Dict[str,Any],SGEntity]]
        assignee=None,  # type: Optional[Union[Dict[str,Any],SGEntity]]
        pipeline_step=None,  # type: Optional[Union[str,Dict[str,Any],SGEntity]]
    ):
        # type: (...) -> List[SGEntity]
        """
        This function is meant as a base for a "tasks" function on a sub class.
        Not every entity has tasks. This is why this function is hidden by default.

        :param names: The names of Tasks to return.
        :param entity: entity to filter by eg. (Shot, Asset, Project,...).
        :param assignee: The assignee of the Tasks to return.
        :param pipeline_step: Name, short name or entity object or the Pipeline Step to filter by.
        :returns: A list of Tasks
        """
        sg_filter = []  # type: List[Union[List[Any],Dict[str,Any]]]

        if assignee is not None:
            if isinstance(assignee, SGEntity):
                assignee = assignee.to_dict()
            sg_filter.append(
                {
                    "filter_operator": "any",
                    "filters": [
                        ["task_assignees", "is", assignee],
                        ["task_assignees.Group.users", "is", assignee],
                    ],
                }
            )

        if names is not None:
            if len(names) == 1:
                names_filter = [
                    "content",
                    "is",
                    names[0],
                ]  # type: Union[List[Any],Dict[str,Any]]
            else:
                names_filter = {"filter_operator": "any", "filters": []}
                for name in names:
                    names_filter["filters"].append(["content", "is", name])
            sg_filter.append(names_filter)

        if entity is not None:
            if isinstance(entity, dict):
                entity_dict = entity
            elif isinstance(entity, SGEntity):
                entity_dict = entity.to_dict()
            else:
                raise TypeError(
                    'The "entity" parameter needs to be one of '
                    "type dict, SGEntity or None."
                )

            if entity_dict["type"] == "Project":
                sg_filter.append(["project", "is", entity_dict])
            else:
                sg_filter.append(["entity", "is", entity_dict])

        if pipeline_step is not None:
            if isinstance(pipeline_step, dict):
                sg_filter.append(["step", "is", pipeline_step])
            elif isinstance(pipeline_step, SGEntity):
                sg_filter.append(["step", "is", pipeline_step.to_dict()])
            elif isinstance(pipeline_step, str):
                sg_filter.append(
                    {
                        "filter_operator": "any",
                        "filters": [
                            ["step.Step.code", "is", pipeline_step],
                            ["step.Step.short_name", "is", pipeline_step],
                        ],
                    }
                )
            else:
                raise TypeError(
                    'The "pipeline_step" parameter needs to be one of '
                    "type str, dict, SGEntity or None."
                )

        return [
            new_entity(self._sg, sg_task)
            for sg_task in self._sg.find("Task", sg_filter)
        ]

    def _versions(
        self,
        entity=None,  # type: Optional[Union[Dict[str,Any],SGEntity]]
        user=None,  # type: Optional[Union[Dict[str,Any],SGEntity]]
        pipeline_step=None,  # type: Optional[Union[str,Dict[str,Any],SGEntity]]
        latest=False,  # type: bool
    ):
        # type: (...) -> List[SGEntity]
        """
        This function is meant as a base for a "versions" function on a sub class.
        Not every entity has tasks. This is why this function is hidden by default.

        :param entity: entity to filter by eg. (Shot, Asset, Project, Task...).
        :param user: The artist assigned to the Versions.
        :param pipeline_step: Name, short name or entity object or the Pipeline Step to filter by.
        :param latest: Whether to return only the latest Version per link/entity.
        :returns: A list of Versions
        """
        sg_filter = []  # type: List[Union[List[Any],Dict[str,Any]]]

        if user is not None:
            if isinstance(user, SGEntity):
                user = user.to_dict()
            sg_filter.append(["user", "is", user])

        if entity is not None:
            if isinstance(entity, dict):
                entity_dict = entity
            elif isinstance(entity, SGEntity):
                entity_dict = entity.to_dict()
            else:
                raise TypeError(
                    'The "entity" parameter needs to be one of '
                    "type dict, SGEntity or None."
                )

            if entity_dict["type"] == "Project":
                sg_filter.append(["project", "is", entity_dict])
            elif entity_dict["type"] == "Task":
                sg_filter.append(["sg_task", "is", entity_dict])
            else:
                sg_filter.append(["entity", "is", entity_dict])

        if pipeline_step is not None:
            if isinstance(pipeline_step, dict):
                sg_filter.append(["sg_task.Task.step", "is", pipeline_step])
            elif isinstance(pipeline_step, SGEntity):
                sg_filter.append(["sg_task.Task.step", "is", pipeline_step.to_dict()])
            elif isinstance(pipeline_step, str):
                sg_filter.append(
                    {
                        "filter_operator": "any",
                        "filters": [
                            ["sg_task.Task.step.Step.code", "is", pipeline_step],
                            ["sg_task.Task.step.Step.short_name", "is", pipeline_step],
                        ],
                    }
                )
            else:
                raise TypeError(
                    'The "pipeline_step" parameter needs to be one of '
                    "type str, dict, SGEntity or None."
                )

        sg_versions = self._sg.find(
            "Version",
            sg_filter,
            ["entity", "created_at"],
        )

        # Sort one more time by name.
        sg_versions.sort(key=lambda pub: pub["entity"]["id"])
        # sort them by date and than by version_number which sorts the latest publish to the
        # last position.
        sg_versions.sort(key=lambda pub: pub["created_at"], reverse=True)

        if latest:
            tmp_list = []
            last_entity = {}  # type: Dict[str,Any]
            for sg_version in sg_versions:
                if sg_version["entity"] == last_entity:
                    continue
                else:
                    last_entity = sg_version["entity"]
                    tmp_list.append(sg_version)
            sg_versions = tmp_list

        return [new_entity(self._sg, sg_version) for sg_version in sg_versions]


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

    def __eq__(self, other):
        # type: (Any) -> bool
        """
        Compare SGSites against each other.
        We consider the Site equal if all these are true:
          - the other instance is a (sub-)class of SGSite
          - the base URL of the Shotgun instances is the same.

        :param other: The other python object to compare to.
        :return: Whether the 2 instances represent the same ShotGrid site.
        """
        return isinstance(other, SGSite) and self._sg.base_url == other.sg.base_url

    def create(self, entity_type, data):
        # type: (str,Dict[str,Any]) -> SGEntity
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
        # type: (...) -> List[SGEntity]
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
        # type: (...) -> Optional[SGEntity]
        """
        The same function as
        :py:meth:`Shotgun.find_one <shotgun_api3:shotgun_api3.shotgun.Shotgun.find_one>` ,
        but it accepts and returns pyshotgrid objects.
        """
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
        # type: (Union[str,int]) -> Optional[SGEntity]
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
        # type: (Optional[List[Union[str,int]]],bool,bool) ->  List[SGEntity]
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
        project=None,  # type: Optional[Union[Dict[str,Any],SGEntity]]
    ):
        # type: (...) ->  Optional[SGEntity]
        """
        :param name_or_id: Name or ID of the PipelineConfiguration.
        :param project: The project that the PipelineConfiguration is attached to.
        :return: A PipelineConfiguration or None.
        """
        base_filter = []  # type: List[List[Any]]
        if name_or_id is not None:
            if isinstance(name_or_id, int):
                sg_pipe_config = self._sg.find_one(
                    "PipelineConfiguration", [["id", "is", name_or_id]]
                )

                if sg_pipe_config:
                    return new_entity(self._sg, sg_pipe_config)
                return None
            else:
                base_filter = [["code", "is", name_or_id]]

        if project is not None:
            if isinstance(project, dict):
                base_filter.append(["project", "is", project])
            elif isinstance(project, SGEntity):
                base_filter.append(["project", "is", project.to_dict()])
            else:
                raise ValueError(
                    'The "project" parameter needs to be '
                    "either a dictionary or a SGEntity."
                )
        sg_pipe_config = self._sg.find_one("PipelineConfiguration", base_filter)

        if sg_pipe_config:
            return new_entity(self._sg, sg_pipe_config)
        return None

    def people(self, only_active=True):
        # type: (bool) ->  List[SGEntity]
        """
        :param only_active: Whether to list only active people or all the people.
        :return: All HumanUsers of this ShotGrid site.
        """
        sg_filter = []
        if only_active:
            sg_filter.append(["sg_status_list", "is", "act"])

        return [
            new_entity(self._sg, sg_user)
            for sg_user in self._sg.find("HumanUser", sg_filter)
        ]


class Field(object):
    """
    This class represents a field on a ShotGrid entity.
    It provides an interface to manage various aspects of a field.
    """

    # Note to developers:
    # The naming convention of this class intentionally leaves out the "SG" in front,
    # since there is a ShotGrid entity that is called "Field".

    def __init__(self, name, entity):
        # type: (str, SGEntity) -> None
        """
        :param name: The name of the field.
        :param entity: The entity that this field is attached to.
        """
        self._name = name
        self._entity = entity
        self._schema = FieldSchema(
            sg=self._entity.sg, entity_type=self._entity.type, field_name=self._name
        )

    def __str__(self):
        # type: () -> str
        return "{} - {} - Entity: {} Entity ID: {}".format(
            self.__class__.__name__, self._name, self.entity.type, self._entity.id
        )

    @property
    def name(self):
        # type: () -> str
        """
        :return: The name of the field.
        """
        return self._name

    @property
    def entity(self):
        # type: () -> SGEntity
        """
        :return: The entity that this field is attached to.
        """
        return self._entity

    def get(self, raw_values=False):
        # type: (bool) -> Any
        """
        :param raw_values: Whether to return the raw dict values or the values converted to
                           pyshotgrid objects.
        :return: The value of the field. Any entities will be automatically converted to
                 pyshotgrid objects.
        """
        value = self._entity.sg.find_one(
            entity_type=self._entity.type,
            filters=[["id", "is", self._entity.id]],
            fields=[self._name],
        ).get(self._name)
        return value if raw_values else convert_value_to_pysg(self._entity.sg, value)

    def set(self, value):
        # type: (Any) -> None
        """
        Set the field to the given value in ShotGrid.

        :param value: The value to set the field to.
        """
        self._entity.sg.update(
            self._entity.type,
            self._entity.id,
            data={self._name: convert_value_to_dict(value)},
        )

    def add(self, values):
        # type: (List[Any]) -> None
        """
        Add some values to this field

        :param values: The value to add to this field.
        """
        self._entity.sg.update(
            self._entity.type,
            self._entity.id,
            data={self._name: convert_value_to_dict(values)},
            multi_entity_update_modes="add",
        )

    def remove(self, values):
        # type: (List[Any]) -> None
        """
        Remove some values from this field.

        :param values: The values to remove from this field.
        """
        self._entity.sg.update(
            self._entity.type,
            self._entity.id,
            data={self._name: convert_value_to_dict(values)},
            multi_entity_update_modes="remove",
        )

    def upload(self, path, display_name=None):
        # type: (str, Optional[str]) -> SGEntity
        """
        Upload a file to this field.

        :param path: The path to the file to upload.
        :param display_name: The display name of the file in ShotGrid.
        :return: The Attachment entity that was created for the uploaded file.
        """
        sg_attachment_id = self._entity.sg.upload(
            entity_type=self._entity.type,
            entity_id=self._entity.id,
            path=path,
            field_name=self._name,
            display_name=display_name,
        )
        return new_entity(self._entity.sg, "Attachment", sg_attachment_id)

    def download(self, path):
        # type: (str) -> None
        """
        Download a file from a field.

        :param path: The path to download to.
        :raises:
            :RuntimeError: When nothing was uploaded to this field.
        """
        sg_attachment = self._entity.sg.find_one(
            self._entity.type, [["id", "is", self._entity.id]], [self._name]
        )[self._name]

        if sg_attachment is None:
            raise RuntimeError(
                'Cannot download file from field "{}" on entity "{}", because there'
                "is nothing uploaded.".format(self.name, self.entity.to_dict())
            )

        # if we can split of a file extension from the given path we assume that the path is the
        # full path with file name to download to. In the other case we assume that the path is
        # the directory to download to and attach the attachment name as the file name to the
        # directory path.
        _, ext = os.path.splitext(path)
        if ext:
            local_file_path = os.path.join(path, sg_attachment["name"])
        else:
            local_file_path = path

        self._entity.sg.download_attachment(
            attachment=sg_attachment, file_path=local_file_path
        )

    @property
    def schema(self):
        # type: () -> FieldSchema
        """
        :return: The schema of this field.
        """
        return self._schema

    @property
    def data_type(self):
        # type: () -> str
        """
        :return: The data type of the field.
        """
        return self._schema.data_type

    @property
    def description(self):
        # type: () -> str
        """
        :return: The description of the field.
        """
        return self._schema.description

    @property
    def display_name(self):
        # type: () -> str
        """
        :return: The display name of the field.
        """
        return self._schema.display_name

    @property
    def properties(self):
        # type: () -> Dict[str,Dict[str,Any]]
        """
        :return: The properties of the field. This strongly depends on the data type of the field.
                 This can for example give you all the possible values of a status field.
        """
        return self._schema.properties

    @property
    def valid_types(self):
        # type: () -> List[str]
        """
        :return: The valid SG entity types for entity- and multi-entity-fields.
        """
        return self._schema.valid_types

    def batch_update_dict(self, value):
        # type: (Any) -> Dict[str,Any]
        """
        :param value: The value to set.
        :returns: A dict that can be used in a shotgun.batch() call to update this field.
                  Useful when you want to collect field changes and set them in one go.
        """
        value = convert_value_to_dict(value)
        return {
            "request_type": "update",
            "entity_type": self._entity.type,
            "entity_id": self._entity.id,
            "data": {self._name: value},
        }


class FieldSchema(object):
    """
    This class represents the schema of a field.
    """

    def __init__(self, sg, entity_type, field_name):
        # type: (shotgun_api3.shotgun.Shotgun, str, str) -> None
        """
        :param sg: The current Shotgun instance this instance uses.
        :param entity_type: The type of the SG entity.
        :param field_name: The name of the Field.
        """
        self.sg = sg
        self.entity_type = entity_type
        self.field_name = field_name

    def __str__(self):
        # type: () -> str
        return "{} - {} - Entity: {}".format(
            self.__class__.__name__, self.field_name, self.entity_type
        )

    def _get_schema(self):
        # type: () -> Dict[str,Dict[str,Any]]
        """
        :return: The schema of this field.
                 For example::

                     {'custom_metadata': {'editable': True, 'value': ''},
                      'data_type': {'editable': False, 'value': 'status_list'},
                      'description': {'editable': True, 'value': ''},
                      'editable': {'editable': False, 'value': True},
                      'entity_type': {'editable': False, 'value': 'Shot'},
                      'mandatory': {'editable': False, 'value': False},
                      'name': {'editable': True, 'value': 'Sound delivery'},
                      'properties': {'default_value': {'editable': True,
                                                       'value': ''},
                                     'display_values': {'editable': False,
                                                        'value': {'dlvr': 'Delivered',
                                                                  'wtg': 'Waiting '
                                                                         'to '
                                                                         'Start'}},
                                     'hidden_values': {'editable': False,
                                                       'value': []},
                                     'summary_default': {'editable': True,
                                                         'value': 'none'},
                                     'valid_values': {'editable': True,
                                                      'value': ['dlvr',
                                                                'wtg']}},
                      'ui_value_displayable': {'editable': False,
                                               'value': True},
                      'unique': {'editable': False, 'value': False},
                      'visible': {'editable': True, 'value': True}}
        """
        return self.sg.schema_field_read(self.entity_type, self.field_name)[
            self.field_name
        ]

    def _update_schema(self, prop, value, project_entity=None):
        # type: (str, Any, Optional[Union[Dict[str,Any],SGEntity]]) -> bool
        """
        Update a property of the field.

        :return: True when the update succeeded.
        """
        return self.sg.schema_field_update(
            self.entity_type,
            self.field_name,
            {prop: value},
            project_entity=convert_value_to_dict(project_entity),
        )

    @property
    def data_type(self):
        # type: () -> str
        """
        :return: The data type of the field.
        """
        return self._get_schema()["data_type"]["value"]

    @data_type.setter
    def data_type(self, value):
        # type: (str) -> None
        """
        Set the data type.

        :param str value:
        """
        self._update_schema("data_type", value)

    @property
    def description(self):
        # type: () -> str
        """
        :return: The description of the field.
        """
        return self._get_schema()["description"]["value"]

    @description.setter
    def description(self, value):
        # type: (str) -> None
        self._update_schema("description", value)

    @property
    def display_name(self):
        # type: () -> str
        """
        :return: The display name of the field.
        """
        return self._get_schema()["name"]["value"]

    @display_name.setter
    def display_name(self, value):
        # type: (str) -> None
        self._update_schema("name", value)

    @property
    def custom_metadata(self):
        # type: () -> str
        """
        :returns: Custom metadata attached to this field.
        """
        return self._get_schema()["custom_metadata"]["value"]

    @custom_metadata.setter
    def custom_metadata(self, value):
        # type: (str) -> None
        self._update_schema("custom_metadata", value)

    @property
    def properties(self):
        # type: () -> Dict[str,Dict[str,Any]]
        """
        :return: The properties of the field. This strongly depends on the data type of the field.
                 This can for example give you all the possible values of a status field.
        """
        return self._get_schema()["properties"]

    @properties.setter
    def properties(self, value):
        # type: (Any) -> None
        self._update_schema("properties", value)

    @property
    def valid_types(self):
        # type: () -> List[str]
        """
        :return: The valid SG entity types for entity- and multi-entity-fields.
        """
        return self._get_schema()["properties"]["valid_types"]["value"]


#: Entity plugins that are registered to pyshotgrid.
__ENTITY_PLUGINS = {}  # type: Dict[str,Type[SGEntity]]
#: The class that represents the ShotGrid site.
__SG_SITE_CLASS = SGSite  # type: Type[SGSite]


def new_entity(sg, *args, **kwargs):
    # type: (shotgun_api3.shotgun.Shotgun, Any, Any) -> SGEntity
    """
    Create a new instance of a pyshotgrid class that represents a ShotGrid entity.
    This function is meant to be used as the main way to create new pyshotgrid instances
    and will always return the correct entity instance that you should work with.

    .. Note::

        This does NOT *create* an entity in Shotgrid. It just gives you a python
        object that *represents* an entity.

    The function can be used in 3 ways which all do the same thing::

        sg_entity = pyshotgrid.new_entity(sg, {"id": 1, "type": "Project"})
        sg_entity = pyshotgrid.new_entity(sg, 1, "Project")
        sg_entity = pyshotgrid.new_entity(sg, entity_id=1, entity_type="Project")

    :param sg: A fully initialized Shotgun instance.
    :return: The pyshotgrid object or None if it could not be converted.
    :raises:
        :ValueError: If entity type and ID could not be extracted from the given values.
    """
    entity_type = None
    entity_id = None
    if args:
        if isinstance(args[0], dict):
            # new_entity(sg, {'id': 1, 'type': 'Project'})
            entity_type = args[0]["type"]
            entity_id = args[0]["id"]
        elif len(args) == 2 and isinstance(args[0], int) and isinstance(args[1], str):
            # new_entity(sg, 1, 'Project')
            entity_id = args[0]
            entity_type = args[1]
    elif kwargs:
        # new_entity(sg, entity_id=1, entity_type='Project')
        if "entity_type" in kwargs and "entity_id" in kwargs:
            entity_type = kwargs["entity_type"]
            entity_id = kwargs["entity_id"]

    if entity_type is not None and entity_id is not None:
        if entity_type in __ENTITY_PLUGINS:
            return __ENTITY_PLUGINS[entity_type](sg, entity_id, entity_type)
        return SGEntity(sg, entity_id, entity_type)
    raise ValueError("Entity type and ID could not be extracted from the given values.")


def new_site(*args, **kwargs):
    # type: (Any, Any) -> SGSite
    """
    This function will create a new :py:class:`pyshotgrid.SGSite <pyshotgrid.sg_site.SGSite>`
    instance that represents a ShotGrid site.
    You can pass in either a shotgun_api3.Shotgun instance or
    the parameters of shotgun_api3.Shotgun itself. So this is equivalent::

        >>> sg = shotgun_api3.Shotgun(base_url='https://example.shotgunstudio.com',
        ...                           script_name='Some User',
        ...                           api_key='$ome_password')
        >>> sg_site = new_site(sg)

        >>> sg_site = new_site(base_url='https://example.shotgunstudio.com',
        ...                    script_name='Some User',
        ...                    api_key='$ome_password')

    :return: A new instance of the pyshotgrid site.
    """
    if args:
        if isinstance(
            args[0], (shotgun_api3.Shotgun, shotgun_api3.lib.mockgun.Shotgun)
        ):
            sg = args[0]
        else:
            sg = shotgun_api3.Shotgun(*args)
    else:
        sg = shotgun_api3.Shotgun(**kwargs)
    return __SG_SITE_CLASS(sg)


def register_pysg_class(pysg_class, shotgrid_type=None):
    # type: (Type[SGEntity], Optional[str]) -> None
    """
    Register a class for a ShotGrid type to pyshotgrid.
    This is best illustrated as by an example: Suppose you have a custom entity setup where you
    have an Episode in each project that collects some sequences of shots. It would be nice to have
    some additional functionality on the ShotGridEntity for episode objects (like a "sequences"
    function that returns all the sequences belonging to that episode). What you would do is to
    create a class SGEpisode that inherits from SGEntity and add all the functionality you
    like to it. After that you call::

        register_plugin(SGEpisode)

    or if you like it more explicitly::

        register_plugin(pysg_class=SGEpisode,
                        shotgrid_type="CustomProjectEntity01")

    This will register the class to pyshotgrid and the `new_entity` function will automatically
    create an "SGEpisode" instance as soon as it encounters an Episode entity. This is also
    true for all queries that happen from a SGEntity. So `sg_project['sg_episodes']` would
    return "SGEpisode" instances as well.

    .. Note::

        Registering a class for an existing entity will overwrite the existing entity class.
        This way you can add/overwrite functionality for the classes that are shipped by default.

    :param pysg_class: The class to use for this entity type.
    :param shotgrid_type: The ShotGrid entity type to register for. If this is None it will be
                          taken from the _DEFAULT_SG_ENTITY_TYPE variable from the given pysg_class.
    """
    global __ENTITY_PLUGINS

    if not issubclass(pysg_class, SGEntity):
        raise TypeError(
            'The given class "{}" needs to inherit from pyshotgrid.SGEntity.'
            "".format(pysg_class)
        )

    if shotgrid_type is None:
        if pysg_class.DEFAULT_SG_ENTITY_TYPE is None:
            raise ValueError("No entity type specified to register for.")
        else:
            shotgrid_type = pysg_class.DEFAULT_SG_ENTITY_TYPE

    __ENTITY_PLUGINS[shotgrid_type] = pysg_class


def register_sg_site_class(sg_site_class):
    # type: (Type[SGSite]) -> None
    """
    Register a class that represents the ShotGrid site.

    .. Note::

        This defaults to the SGSite class, but you can use it to
        overwrite this behaviour.

    :param sg_site_class: The class to use as a fallback.
    """
    global __SG_SITE_CLASS

    if not issubclass(sg_site_class, SGSite):
        raise TypeError(
            'The given class "{}" needs to inherit from pyshotgrid.SGEntity.'
            "".format(sg_site_class)
        )
    __SG_SITE_CLASS = sg_site_class


def convert_fields_to_pysg(sg, fields):
    # type: (shotgun_api3.Shotgun, Dict[str,Any]) -> Dict[str,Any]
    """
    Convert all the values from a fields dict to pysg objects where possible.

    :param sg: A fully initialized Shotgun instance.
    :param fields: A fields dict as returned from a shotgun_api3.Shotgun.find()
                                 call for example.
    :return: The same dict with all values converted to pysg objects where possible.
    """
    return {field: convert_value_to_pysg(sg, value) for field, value in fields.items()}


def convert_fields_to_dicts(fields):
    # type: (Dict[str,Any]) -> Dict[str,Any]
    """
    Convert all the values from a fields dict to simple dictionaries. The counterpart function
    to `func:_convert_fields_to_pysg`.

    :param fields: A fields dict as returned from a shotgun_api3.Shotgun.find()
                                 call for example.
    :return: The same dict with all pysg objects converted to dictionaries.
    """
    return {field: convert_value_to_dict(value) for field, value in fields.items()}


def convert_value_to_dict(value):
    # type: (Any) -> Union[Dict[str,Any],List[Dict[str,Any]]]
    """
    Convert any pysg objects form the given value to simple dictionaries.

    :param value: A field value
    :return: The value with all pysg objects converted to dictionaries.
    """
    if isinstance(value, list):
        tmp = []
        for entity in value:
            if isinstance(entity, SGEntity):
                tmp.append(entity.to_dict())
            else:
                tmp.append(entity)
        return tmp
    elif isinstance(value, SGEntity):
        return value.to_dict()
    else:
        return value


def convert_filters_to_dict(filters):
    # type: (List[List[Any]]) -> List[List[Any]]
    """
    Convert any pysg objects form the given shotgun_api3 filter to simple dictionaries.

    Example::

        >>> person = SGEntity(shotgun_api3.Shotgun('...'), entity_type='HumanUser', entity_id=5)
        >>> convert_filters_to_dict([['user', 'is', person]])
        [['user', 'is', {'type': 'HumanUser', 'id': 5}]]

    :param filters: The filters to convert
    :return: The filter with all pysg objects converted to dictionaries.
    """
    for f in filters:
        if isinstance(f[2], list):
            tmp = []
            for entity in f[2]:
                if isinstance(entity, SGEntity):
                    tmp.append(entity.to_dict())
                else:
                    tmp.append(entity)
            f[2] = tmp
        elif isinstance(f[2], SGEntity):
            f[2] = f[2].to_dict()

    return filters


def convert_value_to_pysg(sg, value):
    # type: (shotgun_api3.Shotgun,Any) -> Any
    """
    Convert the value from a field to pysg object(s) where possible.

    :param sg: A fully initialized Shotgun instance.
    :param value: A field value
    :return: The value converted to pysg object(s) where possible.
    """
    if isinstance(value, list):
        return [new_entity(sg, entity) for entity in value]
    elif isinstance(value, dict) and "type" in value and "id" in value:
        return new_entity(sg, value)
    else:
        return value
