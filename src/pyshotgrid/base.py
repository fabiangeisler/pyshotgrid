import collections

import shotgun_api3


def convert(sg, *args, **kwargs):
    entity_type = None
    entity_id = None
    if args:
        if isinstance(args[0], dict):
            entity_type = args[0]['type']
            entity_id = args[0]['id']
        elif len(args) == 2 and isinstance(args[0], str) and isinstance(args[1], int):
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


class ShotGridEntity(collections.Mapping):
    """
    This class represents a single entity in ShotGrid.

    :ivar shotgun_api3.Shotgun sg:
    :ivar str entity_type:
    :ivar int entity_id:
    """

    def __init__(self, sg, entity_type, entity_id):
        self._sg = sg
        self._type = entity_type
        self._id = entity_id

    def __str__(self):
        return '{}  Type: {}  ID: {} URL: {}'.format(
            self.__class__.__name__, self._type, self._id, self.url)

    @property
    def id(self):
        return self._id

    @property
    def type(self):
        return self._type

    @property
    def sg(self):
        return self._sg

    def __getitem__(self, field):
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

    def __iter__(self):
        sg_entity_fields = self.sg.schema_field_read(self._type)  # ,project_entity=self['project'])
        all_fields = self.sg.find_one(self._type,
                                      [['id', 'is', self._id]],
                                      sg_entity_fields.keys())
        # TODO convert entities to pyshotgrid
        return iter(all_fields)

    def __len__(self):
        sg_entity_fields = self.sg.schema_field_read(self._type)  # ,project_entity=self['project'])
        return len(sg_entity_fields)

    def to_dict(self):
        # noinspection PyUnresolvedReferences
        """
        :returns: The entity as a dict which is ready to consume by the shotgun_api3 methods.
                  .. Note::
                        There are 2 ways to convert the entity to a dict:
                        >>> dict(sg_entity)
                        Creates a dict with all the fields (and calls SG for it)
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
        # TODO convert pyshotgrid values to dicts
        return {"request_type": "update",
                "entity_type": self._type,
                "entity_id": self._id,
                "data": data}

    def batch_set(self, data):
        """
        Set many fields at once on this entity.

        :param dict[str,Any] data: A dict with the fields and values to set.
        :return:
        """
        return self.sg.update(self._type,
                              self._id,
                              data=data)

    def batch_get(self, fields, raw_values=False):
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

    def upload(self, field_name, file_path, display_name=None, tag_list=None):
        """
        Upload a file to a field
        """
        return self.sg.upload(entity_type=self._type,
                              entity_id=self._id,
                              path=file_path,
                              field_name=field_name,
                              display_name=display_name,
                              tag_list=tag_list)

    def download(self, field_name, file_path=None):
        """
        Download a file from a field.
        """
        return self.sg.download_attachment(attachment=self[field_name], file_path=file_path)

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


class SGSite(object):

    @classmethod
    def from_credentials(cls, base_url, script_name, api_key):
        return cls(shotgun_api3.Shotgun(base_url=base_url,
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

        return [SGProject(self.sg, sg_project['id']) for sg_project in sg_projects]


class SGProject(ShotGridEntity):

    def __init__(self, sg, project_id):
        super(SGProject, self).__init__(sg, entity_type='Project', entity_id=project_id)

    def shots(self):
        sg_shots = self.sg.find('Shot', [['project', 'is', {'type': 'Project',
                                                            'id': self.id}]])
        return [SGShot(self.sg, sg_shot['id']) for sg_shot in sg_shots]


class SGShot(ShotGridEntity):

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
        :return:
        """
        base_filter = [['entity', 'is', {'type': 'Shot', 'id': self.id}]]
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

        return [SGPublishedFile(self.sg, sg_publish['id']) for sg_publish in sg_publishes]


class SGPublishedFile(ShotGridEntity):

    def __init__(self, sg, published_file_id):
        super(SGPublishedFile, self).__init__(sg, entity_type='PublishedFile',
                                              entity_id=published_file_id)
