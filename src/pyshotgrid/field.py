import os

from .core import (new_entity,
                   convert_value_to_dict,
                   convert_value_to_pysg)


class Field(object):
    """
    This class represents a field on a ShotGrid entity.
    It provides an interface to manage various aspects of a field.
    """
    # Note to developers:
    # The naming convention of this class intentionally leaves out the "SG" in front,
    # since there is a ShotGrid entity that is called "Field".

    def __init__(self, name, entity):
        """
        :param str name: The name of the field.
        :param SGEntity entity: The entity that this field is attached to.
        """
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

    def get(self, raw_values=False):
        """
        :param bool raw_values: Whether to return the raw dict values or the values converted to
                                pyshotgrid objects.
        :return: The value of the field. Any entities will be automatically converted to
                 pyshotgrid objects.
        :rtype: Any
        """
        value = self._entity.sg.find_one(self._entity.type,
                                         [['id', 'is', self._entity.id]],
                                         [self._name]).get(self._name)
        return value if raw_values else convert_value_to_pysg(self._entity.sg, value)

    def set(self, value):
        """
        Set the field to the given value in ShotGrid.

        :param Any value: The value to set the field to.
        """
        self._entity.sg.update(self._entity.type,
                               self._entity.id,
                               data={self._name: convert_value_to_dict(value)})

    def add(self, values):
        """
        Add some values to this field

        :param list[Any] values: The value to add to this field.
        """
        self._entity.sg.update(self._entity.type,
                               self._entity.id,
                               data={self._name: convert_value_to_dict(values)},
                               multi_entity_update_modes='add')

    def remove(self, values):
        """
        Remove some values from this field.

        :param list[Any] values: The values to remove from this field.
        """
        self._entity.sg.update(self._entity.type,
                               self._entity.id,
                               data={self._name: convert_value_to_dict(values)},
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
        return new_entity(self._entity.sg, "Attachment", sg_attachment_id)

    def download(self, path):
        """
        Download a file from a field.

        :param str path: The path to download to.
        :return:
        :raises:
            :RuntimeError: When nothing was uploaded to this field.
        """
        sg_attachment = self._entity.sg.find_one(
            self._entity.type,
            [["id", "is", self._entity.id]],
            [self._name])[self._name]

        if sg_attachment is None:
            raise RuntimeError('Cannot download file from field "{}" on entity "{}", because there'
                               'is nothing uploaded.'.format(self.name, self.entity.to_dict()))

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
        return self._entity.sg.schema_field_read(self._entity.type, self._name)[self._name]

    def _update_schema(self, prop, value, project_entity=None):
        """
        Update a property of the field.

        :return: True when the update succeeded.
        :rtype: bool
        """
        return self._entity.sg.schema_field_update(self._entity.type,
                                                   self._name,
                                                   {prop: value},
                                                   project_entity=project_entity)

    @property
    def data_type(self):
        """
        :return: The data type of the field.
        :rtype: str
        """
        return self.schema()['data_type']['value']

    @data_type.setter
    def data_type(self, value):
        self._update_schema('data_type', value)

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

    @display_name.setter
    def display_name(self, value):
        self._update_schema('name', value)

    @property
    def custom_metadata(self):
        """
        :return: Custom metadata attached to this field.
        :rtype: str
        """
        return self.schema()['custom_metadata']['value']

    @custom_metadata.setter
    def custom_metadata(self, value):
        self._update_schema('custom_metadata', value)

    @property
    def properties(self):
        """
        :return: The properties of the field. This strongly depends on the data type of the field.
                 This can for example give you all the possible values of a status field.
        :rtype: dict[str,dict[str,Any]]
        """
        return self.schema()['properties']

    @properties.setter
    def properties(self, value):
        self._update_schema('properties', value)

    def batch_update_dict(self, value):
        """
        :param Any value: The value to set.
        :returns: A dict that can be used in a shotgun.batch() call to update this field.
                  Useful when you want to collect field changes and set them in one go.
        :rtype: dict[str,Any]
        """
        value = convert_value_to_dict(value)
        return {"request_type": "update",
                "entity_type": self._entity.type,
                "entity_id": self._entity.id,
                "data": {self._name: value}}
