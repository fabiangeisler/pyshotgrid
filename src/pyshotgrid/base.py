import os.path

import shotgun_api3


def convert(sg, *args, **kwargs):
    """
    Convert a given ShotGrid entity to an instance of a pyshotgrid class.
    The function can be used in 3 ways which all do the same thing:

            convert(sg, {'type': 'Project', 'id': 1})
            convert(sg, 'Project', 1)
            convert(sg, entity_type='Project', entity_id=1)

    :param shotgun_api3.Shotgun sg: A fully initialized Shotgun instance.
    :return: The pyshotgrid object or None if it could not be converted.
    :rtype: ShotGridEntity|None
    """
    entity_type = None
    entity_id = None
    if args:
        if isinstance(args[0], dict):
            # convert(sg, {'type': 'Project', 'id': 1})
            entity_type = args[0]['type']
            entity_id = args[0]['id']
        elif len(args) == 2 and isinstance(args[0], str) and isinstance(args[1], int):
            # convert(sg, 'Project', 1)
            entity_type = args[0]
            entity_id = args[1]
    elif kwargs:
        if 'entity_type' in kwargs and 'entity_id' in kwargs:
            entity_type = kwargs['entity_type']
            entity_id = kwargs['entity_id']

    if entity_type is not None and entity_id is not None:
        mapping = {'Project': SGProject,
                   'Shot': SGShot,
                   'PublishedFile': SGPublishedFile}

        if entity_type in mapping:
            return mapping[entity_type](sg, entity_id)
        else:
            return ShotGridEntity(sg, entity_type, entity_id)


class ShotGridEntity(object):
    """
    An instance of this class represents a single entity in ShotGrid.

    :ivar shotgun_api3.Shotgun sg: A fully initialized instance of shotgun_api3.Shotgun.
    :ivar str entity_type: The ShotGrid type of the entity.
    :ivar int entity_id: The ID of the ShotGrid entity.
    """

    def __init__(self, sg, entity_type, entity_id):
        self._sg = sg
        self._type = entity_type
        self._id = entity_id

    def __str__(self):
        return '{} - Type: {} - ID: {} - URL: {}'.format(
            self.__class__.__name__, self._type, self._id, self.url)

    @property
    def id(self):
        """
        :return: The ID of the ShotGrid entity.
        :rtype: int
        """
        return self._id

    @property
    def type(self):
        """
        :return: The type of the ShotGrid entity.
        :rtype: str
        """
        return self._type

    @property
    def sg(self):
        """
        :return: The Shotgun instance that the entity belongs to.
        :rtype: shotgun_api3.Shotgun
        """
        return self._sg

    @property
    def url(self):
        """
        :return: The ShotGrid URL for this entity.
                 .. Note::
                     This will only work on entities that have a detail view enabled
                     in the system settings.
        :rtype: str
        """
        return '{}/detail/{}/{}'.format(self.sg.base_url, self._type, self._id)

    def __getitem__(self, field):
        """
        Enabling dict notation to query fields of the entity from ShotGrid.
        Values will be automatically converted to pyshotgrid objects.

        :param field:
        :return:
        """
        value = self.sg.find_one(self._type,
                                 [['id', 'is', self._id]],
                                 [field]).get(field)

        if isinstance(value, list):
            return [convert(self._sg, entity) for entity in value]
        elif isinstance(value, dict) and 'type' in value and 'id' in value:
            return convert(self._sg, value)
        else:
            return value

    def __setitem__(self, key, value):
        self.sg.update(self._type,
                       self._id,
                       data={key: value})

    def all_fields(self, project_entity=None, raw_values=False):
        """
        :param dict[str,Any]|ShotGridEntity project_entity: A project entity to filter by.
        :param bool raw_values: Whether to convert entities to pysg objects or not.
        :return: All fields and values from this entity in a dict. If a project entity is given
                 only fields that are visible to the project are returned.
        :rtype: dict[str,Any]
        """
        if isinstance(project_entity, ShotGridEntity):
            project_entity = project_entity.to_dict()

        sg_entity_fields = self.sg.schema_field_read(self._type, project_entity=project_entity)
        fields = [field
                  for field, schema in sg_entity_fields.items()
                  if schema['visible']['value']]
        all_fields = self.sg.find_one(self._type,
                                      [['id', 'is', self._id]],
                                      fields)

        if raw_values:
            return all_fields
        else:
            return self._convert_fields_to_pysg(all_fields)

    def to_dict(self):
        # noinspection PyUnresolvedReferences
        """
        :returns: The entity as a dict which is ready to consume by the shotgun_api3 methods.
                  .. Note::
                        >>> sg_entity.to_dict()
                        Creates a dict with just "type" and "id" (and does not call SG).
        :rtype: dict[str,Any]
        """
        return {'id': self._id, 'type': self._type}

    def batch_set_dict(self, data):
        """
        :param dict[str,Any] data: A dict with the fields and values to set.
        :returns: A dict that can be used in a shotgun.batch() call to update some fields.
                  Useful when you want to collect field changes and set them in one go.
        :rtype: dict
        """
        data = self._convert_fields_to_dicts(data)
        return {"request_type": "update",
                "entity_type": self._type,
                "entity_id": self._id,
                "data": data}

    def set(self, data):
        """
        Set many fields at once on this entity.

        :param dict[str,Any] data: A dict with the fields and values to set.
        :return:
        """
        return self.sg.update(self._type,
                              self._id,
                              data=data)

    def get(self, fields, raw_values=False):
        """
        Set many fields at once on this entity.

        :param list[str] fields: A list of fields to query from this entity.
        :param bool raw_values: Any entities will be converted to pyshotgrid instances.
                                If you set this parameter to True you can turn this behaviour off.
        :return: A dict with the fields and their corresponding values.
        :rtype: dict[str,Any]
        """
        sg_fields = self.sg.find_one(self._type,
                                     [['id', 'is', self._id]],
                                     fields)

        del sg_fields['id']
        del sg_fields['type']

        if raw_values:
            return sg_fields

        result = {}
        for field, value in sg_fields.items():
            if isinstance(value, list):
                result[field] = [convert(self._sg, entity) for entity in value]
            elif isinstance(value, dict) and 'type' in value and 'id' in value:
                result[field] = convert(self._sg, value)
            else:
                result[field] = value
        return result

    def delete(self):
        """
        Delete this entity.
        .. Note::
            The python object that represents this entity does not make sense any more after you
            ran this method and will create errors if you keep calling functions on it.

        :return: Whether the entity was successfully deleted.
        :rtype: bool
        """
        return self._sg.delete(self._type, self._id)

    def schema(self):
        """
        :return: The schema for the current entity.
        """
        return self.sg.schema_entity_read(self._type)

    def field_schema(self, field):
        """
        :return: The schema for the given field.
        """
        return self.sg.schema_field_read(self._type, field)[field]

    def upload(self, field, path, display_name=None):
        """
        Upload a file to a field.

        :param str field: The field to upload to.
        :param str path: The path to the file to upload.
        :param str display_name: The display name of the file in ShotGrid.
        :return: The Attachment entity that was created for the uploaded file.
        :rtype: ShotGridEntity
        """
        sg_attachment_id = self.sg.upload(entity_type=self._type,
                                          entity_id=self._id,
                                          path=path,
                                          field_name=field,
                                          display_name=display_name)
        return convert(self._sg, "Attachment", sg_attachment_id)

    def download(self, field, path):
        """
        Download a file from a field.

        :param str field: The field to download from.
        :param str path: The path to download to.
        :return:
        """
        # TODO What if the field is empty?
        sg_attachment = self._sg.find_one(self._type,
                                          [["id", "is", self._id]],
                                          [field])[field]
        # if we can split of a file extension from the given path we assume that the path is the
        # full path with file name to download to. In the other case we assume that the path is
        # the directory to download to and attach the attachment name as the file name to the
        # directory path.
        _, ext = os.path.splitext(path)
        if ext:
            local_file_path = os.path.join(path, sg_attachment["name"])
        else:
            local_file_path = path

        return self.sg.download_attachment(attachment=sg_attachment,
                                           file_path=local_file_path)

    def _convert_fields_to_pysg(self, fields):
        """
        Convert all the values from a fields dict to pysg objects where possible.

        :param dict[str,Any] fields: A fields dict as returned from a shotgun_api3.Shotgun.find()
                                     call for example.
        :return: The same dict with all values converted to pysg objects where possible.
        :rtype: dict[str,Any]
        """
        result = {}
        for field, value in fields.items():

            if isinstance(value, list):
                result[field] = [convert(self._sg, entity) for entity in value]
            elif isinstance(value, dict) and 'type' in value and 'id' in value:
                result[field] = convert(self._sg, value)
            else:
                result[field] = value

        return result

    @staticmethod
    def _convert_fields_to_dicts(fields):
        """
        Convert all the values from a fields dict to simple dictionaries. The counterpart function
        to `func:_convert_fields_to_pysg`.

        :param dict[str,Any] fields: A fields dict as returned from a shotgun_api3.Shotgun.find()
                                     call for example.
        :return: The same dict with all pysg objects converted to dictionaries.
        :rtype: dict[str,Any]
        """
        result = {}
        for field, value in fields.items():

            if isinstance(value, list):
                tmp = []
                for entity in value:
                    if isinstance(entity, ShotGridEntity):
                        tmp.append(entity.to_dict())
                    else:
                        tmp.append(entity)
                result[field] = tmp
            elif isinstance(value, ShotGridEntity):
                result[field] = value.to_dict()
            else:
                result[field] = value

        return result


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

    def shots(self):
        """
        :return: All the shots from this project.
        :rtype: list[SGShot]
        """
        sg_shots = self.sg.find('Shot', [['project', 'is', {'type': 'Project',
                                                            'id': self.id}]])
        return [convert(self._sg, sg_shot) for sg_shot in sg_shots]


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
        base_filter = [['entity', 'is', self.to_dict()]]
        if pub_types is not None:
            if isinstance(pub_types, list):
                pub_types_filter = {"filter_operator": "any", "filters": []}
                for pub_type in pub_types:
                    pub_types_filter['filters'].append(
                        ['published_file_type.PublishedFileType.code', 'is', pub_type])
            else:
                pub_types_filter = ['published_file_type.PublishedFileType.code', 'is', pub_types]
            base_filter.append(pub_types_filter)

        additional_sg_filter = additional_sg_filter or []
        result_filter = base_filter + additional_sg_filter

        sg_publishes = self.sg.find('PublishedFile',
                                    result_filter,
                                    ['name', 'version_number', 'created_at'])
        if latest:
            # group publishes by "name"
            tmp = {}
            for sg_publish in sg_publishes:
                if sg_publish['name'] in tmp:
                    tmp[sg_publish['name']].append(sg_publish)
                else:
                    tmp[sg_publish['name']] = [sg_publish]

            # sort them by date and than by version_number which sorts the latest publish to the
            # last position.
            result = []
            for publishes in tmp.values():
                publishes.sort(key=lambda pub: (pub['created_at'], pub['version_number']))
                result.append(publishes[-1])

            # Sort one more time by name.
            result.sort(key=lambda pub: pub['name'])

            sg_publishes = result

        return [convert(self._sg, sg_publish) for sg_publish in sg_publishes]


class SGPublishedFile(ShotGridEntity):
    """
    An instance of this class represents a single PublishedFile entity in ShotGrid.

    :ivar shotgun_api3.Shotgun sg: A fully initialized instance of shotgun_api3.Shotgun.
    :ivar int published_file_id: The ID of the PublishedFile entity.
    """

    def __init__(self, sg, published_file_id):
        super(SGPublishedFile, self).__init__(sg, entity_type='PublishedFile',
                                              entity_id=published_file_id)
