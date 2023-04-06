import os
import typing
from typing import Any, Dict, List, Optional, Type, Union  # noqa: F401

if typing.TYPE_CHECKING:
    import shotgun_api3  # noqa: F401

    from .sg_entity import SGEntity  # noqa: F401

from .core import convert_value_to_dict, convert_value_to_pysg, new_entity


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
        # type: (str, Optional[str]) -> Optional[Type[SGEntity]]
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

        # TODO: return the attachment entity object
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

    @data_type.setter
    def data_type(self, value):
        # type: (str) -> None
        self._schema.data_type = value

    @property
    def description(self):
        # type: () -> str
        """
        :return: The description of the field.
        """
        return self._schema.description

    @description.setter
    def description(self, value):
        # type: (str) -> None
        self._schema.description = value

    @property
    def display_name(self):
        # type: () -> str
        """
        :return: The display name of the field.
        """
        return self._schema.display_name

    @display_name.setter
    def display_name(self, value):
        # type: (str) -> None
        self._schema.display_name = value

    @property
    def custom_metadata(self):
        # type: () -> str
        """
        :return: Custom metadata attached to this field.
        """
        return self._schema.custom_metadata

    @custom_metadata.setter
    def custom_metadata(self, value):
        # type: (str) -> None
        self._schema.custom_metadata = value

    @property
    def properties(self):
        # type: () -> Dict[str,Dict[str,Any]]
        """
        :return: The properties of the field. This strongly depends on the data type of the field.
                 This can for example give you all the possible values of a status field.
        """
        return self._schema.properties

    @properties.setter
    def properties(self, value):
        # type: (Any) -> None
        self._schema.properties = value

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
