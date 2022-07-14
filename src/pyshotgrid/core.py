

#: Entity plugins that are registered to pyshotgrid.
__ENTITY_PLUGINS = []
#: Fallback entity class that is used when no match in the __ENTITY_PLUGINS is found.
__ENTITY_FALLBACK_CLASS = None  # type: callable


def convert(sg, *args, **kwargs):
    """
    Convert a given ShotGrid entity to an instance of a pyshotgrid class.
    The function can be used in 3 ways which all do the same thing::

        convert(sg, {'type': 'Project', 'id': 1})
        convert(sg, 'Project', 1)
        convert(sg, entity_type='Project', entity_id=1)

    :param shotgun_api3.Shotgun sg: A fully initialized Shotgun instance.
    :return: The pyshotgrid object or None if it could not be converted.
    :rtype: ShotGridEntity|None
    """
    entity_type = None
    entity_id = None
    if args:
        if isinstance(args[0], dict):
            # convert(sg, {'type': 'Project', 'id': 1})
            entity_type = args[0]['type']
            entity_id = args[0]['id']
        elif len(args) == 2 and isinstance(args[0], str) and isinstance(args[1], int):
            # convert(sg, 'Project', 1)
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


def register_plugin(shotgrid_type, pysg_class, display_name=None):
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

    This will register the class to pyshotgrid and the `convert` function will automatically
    convert to the "SGEpisode" instance as soon as it encounters an Episode entity. This is also
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
    Register a class for a pyshotgrid that will be used when non of the specific entity classes
    have a match.

    .. Note::

        By default this registers the ShotGridEntity class as fallback, but you can use it to
        overwrite this behaviour.

    :param class pysg_class: The class to use as a fallback.
    """
    global __ENTITY_FALLBACK_CLASS
    __ENTITY_FALLBACK_CLASS = pysg_class
