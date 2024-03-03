"""
Main module which collects all important functionality.

Use it like::

    >>> import pyshotgrid

"""

from . import sg_default_entities as sde
from .core import (
    Field,  # noqa: F401
    FieldSchema,  # noqa: F401
    SGEntity,  # noqa: F401
    SGSite,  # noqa: F401
    new_entity,  # noqa: F401
    new_site,  # noqa: F401
    register_pysg_class,
    register_sg_site_class,  # noqa: F401
)

#: The pyshotgrid version number as string
VERSION = "2.0.0"

# Register default pysg plugins
register_pysg_class(sde.SGProject)
register_pysg_class(sde.SGShot)
register_pysg_class(sde.SGAsset)
register_pysg_class(sde.SGTask)
register_pysg_class(sde.SGPublishedFile)
register_pysg_class(sde.SGPlaylist)
register_pysg_class(sde.SGVersion)
register_pysg_class(sde.SGHumanUser)
