
How it works
============

There are two important classes to understand in pyshotgrid:
  - `SGSite` - represents your ShotGrid site and is usually
    your entry point for coding with `pyshotgrid`.
  - `SGEntity` - represents a single entity in Shotgrid.
    It provides a lot of convenience methods to update or query information
    about it from ShotGrid. There are further subclasses that
    add even more functionality.

The SGEntity class
------------------

The `SGEntity` class is the base class for all specific Entity classes.
It represents a single entity from a ShotGrid site and only
stores 3 values:

  - The shotgun_api3.Shotgun instance that is used to get and set all the information from.
  - The ShotGrid entity type
  - The ShotGrid entity ID

All functionality of the `SGEntity` class is based on these three values.
There are some "special" classes that inherit from `SGEntity` to add some
common functionality to common entities in ShotGrid. For example the `SGProject`
class adds a `shots()` function which gives you a list of shots from that project.
To ensure that you are always using the right class you should use the `pyshotgrid.new_entity()`
function which will return the right instance for you.
