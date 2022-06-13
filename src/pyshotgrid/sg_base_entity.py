import os

from .core import convert


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

    def batch_update_dict(self, data):
        """
        :param dict[str,Any] data: A dict with the fields and values to set.
        :returns: A dict that can be used in a shotgun.batch() call to update some fields.
                  Useful when you want to collect field changes and set them in one go.
        :rtype: dict[str,Any]
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

    def _publishes(self, base_filter=None, pub_types=None, latest=False, additional_sg_filter=None):
        """
        This function is meant as a base for a "publishes" function on a sub class. Publishes
        are stored in different fields for each entity and not every entity has a published file.
        This is why this function is hidden by default.

        :param base_filter: The basic sg filter to get the publishes that are associated with
                            this entity.
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
        base_filter = base_filter or []
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
