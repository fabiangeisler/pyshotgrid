
import shotgun_api3

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


class PySG(shotgun_api3.Shotgun):
    # Is this really a good idea?
    """
    Thin wrapper around shotgun_api3.Shotgun
    to extend the CRUD functions to accept and return ShotGridEntity instances.
    """

    def find(self, entity_type, filters, fields=None, order=None, filter_operator=None, limit=0,
             retired_only=False, page=0, include_archived_projects=True,
             additional_filter_presets=None):
        return [ShotGridEntity.from_sg_dict(self, sg_entity)
                for sg_entity in super(PySG, self).find(
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
