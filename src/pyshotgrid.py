"""Main module."""

VERSION = '0.1.0'

import collections
import webbrowser

import shotgun_api3


class ShotGridEntity(collections.Mapping):
    """
    This class represents a single entity in ShotGrid.

    :ivar shotgun_api3.Shotgun sg:
    :ivar str entity_type:
    :ivar int entity_id:
    """

    @classmethod
    def from_sg_dict(cls, sg, sg_dict):
        return cls(sg, entity_type=sg_dict['type'], entity_id=sg_dict['id'])

    def __init__(self, sg, entity_type, entity_id):
        self._sg = sg
        self._type = entity_type
        self._id = entity_id

    def __str__(self):
        return '{}  Type: {}  ID: {}'.format(self.__class__.__name__, self._type, self._id)

    @property
    def id(self):
        return self._id

    @property
    def type(self):
        return self._type

    @property
    def sg(self):
        return self._sg

    def __getattr__(self, item):
        return self[item]

    def __getitem__(self, field):
        value = self.sg.find_one(self._type,
                                 [['id', 'is', self._id]],
                                 [field]).get(field)

        if isinstance(value, list):
            return [ShotGridEntity.from_sg_dict(self.sg, entity) for entity in value]
        elif isinstance(value, dict) and 'type' in value and 'id' in value:
            return ShotGridEntity.from_sg_dict(self.sg, value)
        else:
            return value

    def __setitem__(self, key, value):
        self.sg.update(self._type,
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

    def field_upload(self, field_name, file_path, display_name=None, tag_list=None):
        """
        Upload a file to a field
        """
        return self.sg.upload(entity_type=self._type,
                              entity_id=self._id,
                              path=file_path,
                              field_name=field_name,
                              display_name=display_name,
                              tag_list=tag_list)

    def field_download(self, field_name, file_path=None):
        """
        Download a file from a field
        """
        return self.sg.download_attachment(attachment=self[field_name], file_path=file_path)

    @property
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
        webbrowser.open_new_tab(self.shotgrid_url)


class CachedShotgridEntity(ShotGridEntity):
    """

    """

    @classmethod
    def from_sg_dict(cls, sg, sg_dict, initial_fields=None):
        # FIXME
        return cls(sg, entity_type=sg_dict['type'], entity_id=sg_dict['id'])

    def __init__(self, sg, entity_type, entity_id, initial_fields=None, known_fields=None):
        super(self.__class__).__init__(sg, entity_type, entity_id)
        self._cache = {'type': entity_type,
                       'id': entity_id}
        self._cache.update(known_fields or {})
        if initial_fields is not None:
            self._cache.update(self.sg.find_one(self.type, [['id', 'is', self.id]], initial_fields))

    def __getitem__(self, field):
        if field not in self._cache:
            self._cache[field] = super(self.__class__)[field]
        return self._cache[field]

    def __iter__(self):
        # FIXME should iter over all fields
        return iter(self._cache)

    def __len__(self):
        # FIXME should count all fields
        return len(self._cache)

    def clear_cache(self):
        for key in self._cache:
            if key not in ['type', 'id']:
                del self._cache[key]

    def convert_to_uncached_entity(self):
        """
        Convert the instance to a `ShotGridEntity`.
        """
        # TODO


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


class PyShotGrid(shotgun_api3.Shotgun):
    # Is this really a good idea?
    """
    Thin wrapper around shotgun_api3.Shotgun
    to extend the CRUD functions to accept and return ShotGridEntity instances.
    """

    def find(self, entity_type, filters, fields=None, order=None, filter_operator=None, limit=0,
             retired_only=False, page=0, include_archived_projects=True,
             additional_filter_presets=None):
        return [ShotGridEntity.from_sg_dict(self, sg_entity)
                for sg_entity in super(PyShotGrid, self).find(
                entity_type=entity_type,
                filters=filters,
                fields=fields,
                order=order,
                filter_operator=filter_operator,
                limit=limit,
                retired_only=retired_only,
                page=page,
                include_archived_projects=include_archived_projects,
                additional_filter_presets=additional_filter_presets)]
