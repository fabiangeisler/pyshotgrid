User Guide
==========

Using `pyshotgrid` is straight forward and this guide will give teach you the basics on how
to use it under the most common scenarios.

Using `pyshotgrid` with ShotGrid Toolkit
----------------------------------------

After you made `pyshotgrid` accessible in ShotGrid Toolkit the best way to use it is to convert
any entity to a `pyshotgrid` object instance. What you need for this is
a shotgun_api3.Shotgun instance (which conveniently is present almost everywhere in SGTK),
the type and the id of the entity. These parameters will be passed
to the `pyshotgrid.new_entity` method, which returns you the object you want to work with.
Conveniently the method accepts 3 ways of passing arguments to it:

.. code-block:: python

    import pyshotgrid as pysg

    # These 3 lines all do the same thing: Initializing an entity instance of the Project with ID 1.
    sg_entity = pysg.new_entity(sg, {'type': 'Project', 'id': 1})
    sg_entity = pysg.new_entity(sg, 'Project', 1)
    sg_entity = pysg.new_entity(sg, entity_type='Project', entity_id=1)


Using `pyshotgrid` in a standalone application
----------------------------------------------
