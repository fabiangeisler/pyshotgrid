from .core import (new_entity,
                   new_site,
                   convert_fields_to_pysg,
                   convert_fields_to_dicts)
from .field import Field


class SGEntity(object):
    """
    An instance of this class represents a single entity in ShotGrid.
    """

    def __init__(self, sg, entity_type, entity_id):
        """
        :param shotgun_api3.shotgun.Shotgun sg:
            A fully initialized instance of shotgun_api3.Shotgun.
        :param str entity_type: The ShotGrid type of the entity.
        :param int entity_id: The ID of the ShotGrid entity.
        """
        self._sg = sg  # :type: shotgun_api3.shotgun.Shotgun
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
        :rtype: shotgun_api3.shotgun.Shotgun
        """
        return self._sg

    @property
    def site(self):
        """
        :return: The pyshotgrid site for this entity.
        :rtype: SGSite
        """
        return new_site(self._sg)

    @property
    def url(self):
        """
        :return: The ShotGrid URL for this entity.

            .. note::

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
            return convert_fields_to_pysg(self._sg, all_fields)

    def to_dict(self):
        # noinspection PyUnresolvedReferences
        """
        Creates a dict with just "type" and "id" (and does not call SG).

        Example::

            >>> sg_entity.to_dict()
            {'type': 'CustomEntity01', 'id': 1}

        :returns: The entity as a dict which is ready to consume by the shotgun_api3 methods.

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
                "data": convert_fields_to_dicts(data)}

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
                              data=convert_fields_to_dicts(data),
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
        else:
            return convert_fields_to_pysg(self._sg, sg_fields)

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

        return [new_entity(self._sg, sg_publish) for sg_publish in sg_publishes]
