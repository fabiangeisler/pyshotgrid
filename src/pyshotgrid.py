"""Main module."""

__version__ = '0.1.0'

import collections
import copy
import webbrowser


class CachedShotgridEntity(collections.Mapping):
    """

    """

    @classmethod
    def from_dict(cls, sg, sg_dict):
        return cls(sg, entity_type=sg_dict['type'], entity_id=sg_dict['id'])

    def __init__(self, sg, entity_type, entity_id, initial_fields=None):
        self.sg = sg
        self._cache = {'type': entity_type,
                       'id': entity_id}

    def __repr__(self):
        # FIXME
        return '{}()'.format(self.__class__.__name__)

    def __getattr__(self, item):
        return self[item]

    def __getitem__(self, field):
        if field not in self._cache:
            value = self.sg.find_one(self._cache['type'],
                                     [['id', 'is', self._cache['id']]],
                                     [field])[field]
            self._cache[field] = value
        return self._cache[field]

    def __iter__(self):
        return iter(self._cache)

    def __len__(self):
        return len(self._cache)

    def clear_cache(self):
        for key in self._cache:
            if key not in ['type', 'id']:
                del self._cache[key]

    def to_dict(self):
        """
        :returns: a plain dictionary.
        :rtype: dict[str,Any]
        """
        return copy.copy(self._cache)


class ShotGridEntity(collections.Mapping):
    """

    :ivar shotgun_api3.Shotgun sg:
    :ivar str entity_type:
    :ivar int entity_id:
    """

    @classmethod
    def from_sg_dict(cls, sg, sg_dict):
        return cls(sg, entity_type=sg_dict['type'], entity_id=sg_dict['id'])

    def __init__(self, sg, entity_type, entity_id):
        self.sg = sg
        self._type = entity_type
        self._id = entity_id

    def __repr__(self):
        # FIXME
        return '{}()'.format(self.__class__.__name__)

    @property
    def id(self):
        return self._id

    @property
    def type(self):
        return self._type

    def __getattr__(self, item):
        return self[item]

    def __getitem__(self, field):
        # We allow to optionally leave out the "sg_" prefix from the field names.
        # To achieve this we query both field names all the time and see which one is present
        # and return the correct one.
        if field.startswith('sg_'):
            fields = [field, field[-3:]]
        else:
            fields = [field, 'sg_' + field]

        sg_entity = self.sg.find_one(self._type,
                                     [['id', 'is', self._id]],
                                     fields)

        if field in sg_entity:
            value = sg_entity[field]
        elif 'sg_' + field in sg_entity:
            value = sg_entity['sg_' + field]
        else:
            raise KeyError('{} has no field {}'.format(self._type, field))

        if isinstance(value, list):
            return [ShotGridEntity.from_sg_dict(self.sg, entity) for entity in value]
        elif isinstance(value, dict) and 'type' in value and 'id' in value:
            return ShotGridEntity.from_sg_dict(self.sg, value)
        else:
            return value

    def __setitem__(self, key, value):
        return self.sg.update(self._type,
                              self._id,
                              data={key: value})

    def __iter__(self):
        sg_entity_fields = self.sg.schema_field_read(self._type)  # , project_entity=self.project)
        all_fields = self.sg.find_one(self._type,
                                      [['id', 'is', self._id]],
                                      sg_entity_fields.keys())
        return iter(all_fields)

    def __len__(self):
        sg_entity_fields = self.sg.schema_field_read(self._type)  # ,project_entity=self.project)
        return len(sg_entity_fields)

    def schema_field_read(self, field):
        """
        :return: The schema for the given field.
        """
        return self.sg.schema_field_read(self._type, field)[field]

    def schema(self):
        """
        :return: The schema for the current entity.
        """
        return self.sg.schema_entity_read(self._type)

    def upload(self):
        """
        Upload a file to a field
        """
        # TODO

    def download(self):
        """
        Download a file from a field
        """
        # TODO

    def shotgrid_url(self):
        """
        :return: The ShotGrid URL for this entity.
        :rtype: str
        """
        return '{}/detail/{}/{}'.format(self.sg.base_url, self._type, self._id)

    def open_shotgrid_url(self):
        """
        Open the ShotGrid details page in a new browser tab.
        """
        webbrowser.open_new_tab(self.shotgrid_url())


def find(sg, entity_type, filters, fields=None, order=None, filter_operator=None, limit=0,
         retired_only=False, page=0, include_archived_projects=True,
         additional_filter_presets=None):
    """
    :param shotgun_api3.Shotgun sg:
    """
    return [ShotGridEntity.from_sg_dict(sg, sg_entity)
            for sg_entity in sg.find(entity_type=entity_type,
                                     filters=filters,
                                     fields=fields,
                                     order=order,
                                     filter_operator=filter_operator,
                                     limit=limit,
                                     retired_only=retired_only,
                                     page=page,
                                     include_archived_projects=include_archived_projects,
                                     additional_filter_presets=additional_filter_presets)]


def find_one(sg, entity_type, filters, fields=None, order=None, filter_operator=None, limit=0,
             retired_only=False, page=0, include_archived_projects=True,
             additional_filter_presets=None):
    """

    """
    return find(sg=sg,
                entity_type=entity_type,
                filters=filters,
                fields=fields,
                order=order,
                filter_operator=filter_operator,
                limit=limit,
                retired_only=retired_only,
                page=page,
                include_archived_projects=include_archived_projects,
                additional_filter_presets=additional_filter_presets)[0]
