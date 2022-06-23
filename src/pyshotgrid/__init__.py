"""Main module."""

from .core import *
from .sg_entity import SGEntity
from .sg_site import SGSite
from .sg_default_entities import *

#: The pyshotgrid version number as string
VERSION = '0.1.0'

register_fallback_pysg_class(SGEntity)
# Register default pysg plugins
register_plugin('Project', SGProject)
register_plugin('Shot', SGShot)
register_plugin('PublishedFile', SGPublishedFile)
