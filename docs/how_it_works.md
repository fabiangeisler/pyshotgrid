# How it works

There are two important classes to understand in pyshotgrid:
- [SGSite](#pyshotgrid.core.SGSite) - represents your ShotGrid site and is usually
  your entry point for coding with `pyshotgrid`.
- [SGEntity](#pyshotgrid.core.SGEntity) - represents a single entity in Shotgrid.
  It provides a lot of convenience methods to update or query information
  about it from ShotGrid. There are further subclasses that
  add even more functionality.

## The SGEntity class

The [SGEntity](#pyshotgrid.core.SGEntity) class is the base class for all specific
Entity classes. It represents a single entity from a ShotGrid site and only stores 3 values:

- The shotgun_api3.Shotgun instance that is used to get and set all the information from.
- The ShotGrid entity type
- The ShotGrid entity ID

All functionality of the [SGEntity](#pyshotgrid.core.SGEntity) class is based on these
three values. There are some "special" classes that inherit from
[SGEntity](#pyshotgrid.core.SGEntity) to add some common functionality to common entities
in ShotGrid. For example the [SGProject](#pyshotgrid.sg_default_entities.SGProject) class
adds a [shots()](#pyshotgrid.sg_default_entities.SGProject.shots) function which gives
you a list of shots from that project. To ensure that you are always using the right class you
should use the [pyshotgrid.new_entity](#pyshotgrid.core.new_entity) function which will
return the right instance for you.
