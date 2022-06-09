"""Main module."""

from .base import *

#: The pyshotgrid version number as string
VERSION = '0.1.0'

# Register default pysg plugins
register_plugin('Project', SGProject)
register_plugin('Shot', SGShot)
register_plugin('PublishedFile', SGPublishedFile)
