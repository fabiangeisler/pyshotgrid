import os

from .core import convert
from .sg_site import SGSite


class SGEntity(object):
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
    def site(self):
        """
        :return: The pyshotgrid site for this entity.
        :rtype: pyshotgrid.SGSite
        """
        return SGSite(sg=self._sg)

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

        :param str field: The field to query.
        :return: The value of the field. Any entities will be automatically converted to
                 pyshotgrid objects.
        """
        return Field(name=field, entity=self)

    def __setitem__old(self, field, value):
        """
        Set any field to the given value in ShotGrid via pythons dict notation.

        :param str field: The field to set.
        :param Any value: The value to set the field to.
        """
        self.sg.update(self._type,
                       self._id,
                       data={field: self.convert_value_to_dict(value)})

    def fields(self, project_entity=None):
        """
        :param dict[str,Any]|SGEntity|None project_entity: A project entity to filter by.
        :return: All fields from this entity. If a project entity is given
                 only fields that are visible to the project are returned.
        :rtype: list[Field]
        """
        if isinstance(project_entity, self.__class__):
            project_entity = project_entity.to_dict()

        sg_entity_fields = self.sg.schema_field_read(self._type, project_entity=project_entity)
        fields = [field
                  for field, schema in sg_entity_fields.items()
                  if schema['visible']['value']]

        return [Field(name=field, entity=self) for field in fields]

    def all_field_values(self, project_entity=None, raw_values=False):
        """
        :param dict[str,Any]|SGEntity project_entity: A project entity to filter by.
        :param bool raw_values: Whether to convert entities to pysg objects or not.
        :return: All fields and values from this entity in a dict. If a project entity is given
                 only fields that are visible to the project are returned.
        :rtype: dict[str,Any]
        """
        if isinstance(project_entity, self.__class__):
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
            return self.convert_fields_to_pysg(all_fields)

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
        return {"request_type": "update",
                "entity_type": self._type,
                "entity_id": self._id,
                "data": self.convert_fields_to_dicts(data)}

    def set(self, data, multi_entity_update_modes=None):
        """
        Set many fields at once on this entity.

        :param dict[str,Any] data: A dict with the fields and values to set.
        :param dict multi_entity_update_modes: Optional dict indicating what update mode to use
            when updating a multi-entity link field. The keys in the dict are the fields to set
            the mode for, and the values from the dict are one of ``set``, ``add``, or ``remove``.
            Defaults to ``set``.
            ::

                multi_entity_update_modes={"shots": "add", "assets": "remove"}
        :return:
        """
        return self.sg.update(self._type,
                              self._id,
                              data=self.convert_fields_to_dicts(data),
                              multi_entity_update_modes=multi_entity_update_modes)

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
        return self.sg.schema_entity_read()[self._type]

    def field_schemas(self):
        """
        :return: The schemas of all the entity fields.
        """
        return self.sg.schema_field_read(self._type)

    def convert_fields_to_pysg(self, fields):
        """
        Convert all the values from a fields dict to pysg objects where possible.

        :param dict[str,Any] fields: A fields dict as returned from a shotgun_api3.Shotgun.find()
                                     call for example.
        :return: The same dict with all values converted to pysg objects where possible.
        :rtype: dict[str,Any]
        """
        return {field: self.convert_value_to_pysg(value)
                for field, value in fields.items()}

    def convert_fields_to_dicts(self, fields):
        """
        Convert all the values from a fields dict to simple dictionaries. The counterpart function
        to `func:_convert_fields_to_pysg`.

        :param dict[str,Any] fields: A fields dict as returned from a shotgun_api3.Shotgun.find()
                                     call for example.
        :return: The same dict with all pysg objects converted to dictionaries.
        :rtype: dict[str,Any]
        """
        return {field: self.convert_value_to_dict(value)
                for field, value in fields.items()}

    def convert_value_to_dict(self, value):
        """
        Convert any pysg objects form the given value to simple dictionaries.

        :param Any value: A field value
        :return: The value with all pysg objects converted to dictionaries.
        :rtype: dict[str,Any]
        """
        if isinstance(value, list):
            tmp = []
            for entity in value:
                if isinstance(entity, self.__class__):
                    tmp.append(entity.to_dict())
                else:
                    tmp.append(entity)
            return tmp
        elif isinstance(value, self.__class__):
            return value.to_dict()
        else:
            return value

    def convert_value_to_pysg(self, value):
        """
        Convert the value from a field to pysg object(s) where possible.

        :param Any value: A field value
        :return: The value converted to pysg object(s) where possible.
        :rtype: Any
        """
        if isinstance(value, list):
            return [convert(self._sg, entity) for entity in value]
        elif isinstance(value, dict) and 'type' in value and 'id' in value:
            return convert(self._sg, value)
        else:
            return value

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


class Field(object):
    """
    This class represents a field on a ShotGrid entity.
    It provides an interface to manage various aspects of a field.

    :ivar str name: The name of the field.
    :ivar SGEntity entity: The entity that this field is attached to.
    """
    def __init__(self, name, entity):
        self._name = name
        self._entity = entity

    @property
    def name(self):
        """
        :return: The name of the field.
        :rtype: str
        """
        return self._name

    @property
    def entity(self):
        """
        :return: The entity that this field is attached to.
        :rtype: SGEntity
        """
        return self._entity

    def get(self):
        """
        :return: The value of the field. Any entities will be automatically converted to
                 pyshotgrid objects.
        :rtype: Any
        """
        value = self._entity.sg.find_one(self._entity.type,
                                         [['id', 'is', self._entity.id]],
                                         [self._name]).get(self._name)
        return self._entity.convert_value_to_pysg(value)

    def set(self, value):
        """
        Set the field to the given value in ShotGrid.

        :param Any value: The value to set the field to.
        """
        self._entity.sg.update(self._entity.type,
                               self._entity.id,
                               data={self._name: self._entity.convert_value_to_dict(value)})

    def add(self, values):
        """
        Add some values to this field

        :param list[Any] values: The value to add to this field.
        """
        self._entity.sg.update(self._entity.type,
                               self._entity.id,
                               data={self._name: self._entity.convert_value_to_dict(values)},
                               multi_entity_update_modes='add')

    def remove(self, values):
        """
        Remove some values from this field.

        :param list[Any] values: The values to remove from this field.
        """
        self._entity.sg.update(self._entity.type,
                               self._entity.id,
                               data={self._name: self._entity.convert_value_to_dict(values)},
                               multi_entity_update_modes='remove')

    def upload(self, path, display_name=None):
        """
        Upload a file to this field.

        :param str path: The path to the file to upload.
        :param str display_name: The display name of the file in ShotGrid.
        :return: The Attachment entity that was created for the uploaded file.
        :rtype: SGEntity
        """
        sg_attachment_id = self._entity.sg.upload(
            entity_type=self._entity.type,
            entity_id=self._entity.id,
            path=path,
            field_name=self._name,
            display_name=display_name)
        return convert(self._entity.sg, "Attachment", sg_attachment_id)

    def download(self, path):
        """
        Download a file from a field.

        :param str path: The path to download to.
        :return:
        """
        # TODO What if the field is empty?
        sg_attachment = self._entity.sg.find_one(
            self._entity.type,
            [["id", "is", self._entity.id]],
            [self._name])[self._name]
        # if we can split of a file extension from the given path we assume that the path is the
        # full path with file name to download to. In the other case we assume that the path is
        # the directory to download to and attach the attachment name as the file name to the
        # directory path.
        _, ext = os.path.splitext(path)
        if ext:
            local_file_path = os.path.join(path, sg_attachment["name"])
        else:
            local_file_path = path

        return self._entity.sg.download_attachment(
            attachment=sg_attachment,
            file_path=local_file_path)

    def schema(self):
        """
        :return: The schema of this field.
                 For example:

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
                       'visible': {'editable': True, 'value': True}},
        """
        return self._entity.sg.schema_field_read(self._entity.type, self._name)[self._name]

    @property
    def data_type(self):
        """
        :return: The data type of the field.
        :rtype: str
        """
        return self.schema()['data_type']['value']

    @property
    def description(self):
        """
        :return: The description of the field.
        :rtype: str
        """
        return self.schema()['description']['value']

    @property
    def display_name(self):
        """
        :return: The display name of the field.
        :rtype: str
        """
        return self.schema()['name']['value']

    @property
    def properties(self):
        """
        :return: The properties of the field. This strongly depends on the data type of the field.
                 This can for example give you all the possible values of a status field.
        :rtype: dict[str,dict[str,Any]]
        """
        return self.schema()['properties']

    def batch_update_dict(self, value):
        """
        :param Any value: The value to set.
        :returns: A dict that can be used in a shotgun.batch() call to update this field.
                  Useful when you want to collect field changes and set them in one go.
        :rtype: dict[str,Any]
        """
        value = self._entity.convert_value_to_dict(value)
        return {"request_type": "update",
                "entity_type": self._entity.type,
                "entity_id": self._entity.id,
                "data": {self._name: value}}
