"""Main module."""

from .core import convert, register_plugin, register_fallback_pysg_class  # noqa: F401
from .sg_entity import SGEntity
from .sg_site import SGSite  # noqa: F401
from . import sg_default_entities as sde

#: The pyshotgrid version number as string
VERSION = '0.1.0'

register_fallback_pysg_class(SGEntity)
# Register default pysg plugins
register_plugin('Project', sde.SGProject)
register_plugin('Shot', sde.SGShot)
register_plugin('Task', sde.SGTask)
register_plugin('PublishedFile', sde.SGPublishedFile)
register_plugin('HumanUser', sde.SGHumanUser)
