import shotgun_api3

#: Entity plugins that are registered to pyshotgrid.
__ENTITY_PLUGINS = []
#: Fallback entity class that is used when no match in the __ENTITY_PLUGINS is found.
__ENTITY_FALLBACK_CLASS = None
#: The class that represents the ShotGrid site.
__SG_SITE_CLASS = None


def new_entity(sg, *args, **kwargs):
    """
    Create a new instance of a pyshotgrid class that represents a ShotGrid entity.

    .. Note::

        This does NOT *create* an entity in Shotgrid. It just gives you a python
        object that *represents* an entity.

    The function can be used in 3 ways which all do the same thing::

        new_entity(sg, {'type': 'Project', 'id': 1})
        new_entity(sg, 'Project', 1)
        new_entity(sg, entity_type='Project', entity_id=1)

    :param shotgun_api3.shotgun.Shotgun sg: A fully initialized Shotgun instance.
    :return: The pyshotgrid object or None if it could not be converted.
    :rtype: SGEntity|None
    """
    entity_type = None
    entity_id = None
    if args:
        if isinstance(args[0], dict):
            # new_entity(sg, {'type': 'Project', 'id': 1})
            entity_type = args[0]['type']
            entity_id = args[0]['id']
        elif len(args) == 2 and isinstance(args[0], str) and isinstance(args[1], int):
            # new_entity(sg, 'Project', 1)
            entity_type = args[0]
            entity_id = args[1]
    elif kwargs:
        if 'entity_type' in kwargs and 'entity_id' in kwargs:
            entity_type = kwargs['entity_type']
            entity_id = kwargs['entity_id']

    if entity_type is not None and entity_id is not None:

        for entity_plugin in __ENTITY_PLUGINS:
            if entity_type in [entity_plugin['shotgrid_type'], entity_plugin['display_name']]:
                return entity_plugin['pysg_class'](sg, entity_id)
        # noinspection PyCallingNonCallable
        return __ENTITY_FALLBACK_CLASS(sg, entity_type, entity_id)


def new_site(*args, **kwargs):
    """
    This function will create a new pyshotgrid SGSite instance that represents a
    ShotGrid site. You can pass in either a shotgun_api3.Shotgun instance or
    the parameters of shotgun_api3.Shotgun itself. So this is equivalent::

        >>> sg = shotgun_api3.Shotgun(base_url='https://example.shotgunstudio.com',
        ...                           script_name='Some User',
        ...                           api_key='$ome_password')
        >>> sg_site = new_site(sg)

        >>> sg_site = new_site(base_url='https://example.shotgunstudio.com',
        ...                    script_name='Some User',
        ...                    api_key='$ome_password')

    :return: A new instance of the pyshotgrid site.
    :rtype: SGSite|None
    """
    if args:
        if isinstance(args[0], (shotgun_api3.Shotgun, shotgun_api3.lib.mockgun.Shotgun)):
            sg = args[0]
        else:
            sg = shotgun_api3.Shotgun(*args)
    else:
        sg = shotgun_api3.Shotgun(**kwargs)
    return __SG_SITE_CLASS(sg)


def register_pysg_class(shotgrid_type, pysg_class, display_name=None):
    """
    Register a class for a ShotGrid type to pyshotgrid.
    This is best illustrated as by an example: Suppose you have a custom entity setup where you
    have an Episode in each project that collects some sequences of shots. It would be nice to have
    some additional functionality on the ShotGridEntity for episode objects (like a "sequences"
    function that returns all the sequences belonging to that episode). What you would do is to
    create a class SGEpisode that inherits from ShotGridEntity and add all the functionality you
    like to it. After that you call::

        register_plugin(shotgrid_type="CustomProjectEntity01",
                        pysg_class=SGEpisode,
                        display_name='Episode')

    This will register the class to pyshotgrid and the `new_entity` function will automatically
    create an "SGEpisode" instance as soon as it encounters an Episode entity. This is also
    true for all queries that happen from a ShotGridEntity. So `sg_project['sg_episodes']` would
    return "SGEpisode" instances as well.

    .. Note::

        Registering a class for an existing entity will overwrite the existing entity class.
        This way you can add/overwrite functionality for the classes that are shipped by default.

    :param str shotgrid_type: The ShotGrid entity type to register for.
    :param class pysg_class: The class to use for this entity type.
    :param str|None display_name: The display name of the entity type. If this is None, the display
                                  name will be the same as the shotgrid_type parameter.
    """
    global __ENTITY_PLUGINS

    __ENTITY_PLUGINS.append({
        'shotgrid_type': shotgrid_type,
        'pysg_class': pysg_class,
        'display_name': display_name or shotgrid_type,
    })


def register_fallback_pysg_class(pysg_class):
    """
    Register a class for shotgrid entities that will be used when none of the specific
    entity classes have a match.

    .. Note::

        By default this registers the SGEntity class as fallback, but you can use it to
        overwrite this behaviour.

    :param class pysg_class: The class to use as a fallback.
    """
    global __ENTITY_FALLBACK_CLASS
    __ENTITY_FALLBACK_CLASS = pysg_class


def register_sg_site_class(sg_site_class):
    """
    Register a class that represents the ShotGrid site.

    .. Note::

        This defaults to the SGSite class, but you can use it to
        overwrite this behaviour.

    :param class sg_site_class: The class to use as a fallback.
    """
    global __SG_SITE_CLASS
    __SG_SITE_CLASS = sg_site_class


def convert_fields_to_pysg(sg, fields):
    """
    Convert all the values from a fields dict to pysg objects where possible.

    :param shotgun_api3.Shotgun sg: A fully initialized Shotgun instance.
    :param dict[str,Any] fields: A fields dict as returned from a shotgun_api3.Shotgun.find()
                                 call for example.
    :return: The same dict with all values converted to pysg objects where possible.
    :rtype: dict[str,Any]
    """
    return {field: convert_value_to_pysg(sg, value)
            for field, value in fields.items()}


def convert_fields_to_dicts(fields):
    """
    Convert all the values from a fields dict to simple dictionaries. The counterpart function
    to `func:_convert_fields_to_pysg`.

    :param dict[str,Any] fields: A fields dict as returned from a shotgun_api3.Shotgun.find()
                                 call for example.
    :return: The same dict with all pysg objects converted to dictionaries.
    :rtype: dict[str,Any]
    """
    return {field: convert_value_to_dict(value)
            for field, value in fields.items()}


def convert_value_to_dict(value):
    """
    Convert any pysg objects form the given value to simple dictionaries.

    :param Any value: A field value
    :return: The value with all pysg objects converted to dictionaries.
    :rtype: dict[str,Any]
    """
    if isinstance(value, list):
        tmp = []
        for entity in value:
            if isinstance(entity, __ENTITY_FALLBACK_CLASS):
                tmp.append(entity.to_dict())
            else:
                tmp.append(entity)
        return tmp
    elif isinstance(value, __ENTITY_FALLBACK_CLASS):
        return value.to_dict()
    else:
        return value


def convert_filters_to_dict(filters):
    """
    Convert any pysg objects form the given shotgun_api3 filter to simple dictionaries.

    Example::

        >>> convert_filters_to_dict([['user', 'is', SGHumanUser(sg, id=5)]])
        [['user', 'is', {'type': 'HumanUser', 'id': 5}]]

    :param list[list] filters: The filters to convert
    :return: The filter with all pysg objects converted to dictionaries.
    :rtype: list[list]
    """
    for f in filters:
        if isinstance(f[2], list):
            tmp = []
            for entity in f[2]:
                if isinstance(entity, __ENTITY_FALLBACK_CLASS):
                    tmp.append(entity.to_dict())
                else:
                    tmp.append(entity)
            f[2] = tmp
        elif isinstance(f[2], __ENTITY_FALLBACK_CLASS):
            f[2] = f[2].to_dict()

    return filters


def convert_value_to_pysg(sg, value):
    """
    Convert the value from a field to pysg object(s) where possible.

    :param shotgun_api3.Shotgun sg: A fully initialized Shotgun instance.
    :param Any value: A field value
    :return: The value converted to pysg object(s) where possible.
    :rtype: Any
    """
    if isinstance(value, list):
        return [new_entity(sg, entity) for entity in value]
    elif isinstance(value, dict) and 'type' in value and 'id' in value:
        return new_entity(sg, value)
    else:
        return value
