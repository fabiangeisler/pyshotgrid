"""
Main module which collects all important functionality.

Use it like::

    >>> import pyshotgrid

"""

from .core import (new_entity,  # noqa: F401
                   new_site,  # noqa: F401
                   register_pysg_class,
                   register_fallback_pysg_class,
                   register_sg_site_class)
from .sg_entity import SGEntity, Field  # noqa: F401
from .sg_site import SGSite  # noqa: F401
from . import sg_default_entities as sde

#: The pyshotgrid version number as string
VERSION = '0.7.0'

register_sg_site_class(SGSite)
register_fallback_pysg_class(SGEntity)
# Register default pysg plugins
register_pysg_class('Project', sde.SGProject)
register_pysg_class('Shot', sde.SGShot)
register_pysg_class('Asset', sde.SGAsset)
register_pysg_class('Task', sde.SGTask)
register_pysg_class('PublishedFile', sde.SGPublishedFile)
register_pysg_class('Playlist', sde.SGPlaylist)
register_pysg_class('Version', sde.SGVersion)
register_pysg_class('HumanUser', sde.SGHumanUser)
