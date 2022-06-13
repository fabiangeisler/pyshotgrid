"""Main module."""

from .core import *
from .sg_base_entity import ShotGridEntity
from .sg_entities import *

#: The pyshotgrid version number as string
VERSION = '0.1.0'

register_fallback_pysg_class(ShotGridEntity)
# Register default pysg plugins
register_plugin('Project', SGProject)
register_plugin('Shot', SGShot)
register_plugin('PublishedFile', SGPublishedFile)
