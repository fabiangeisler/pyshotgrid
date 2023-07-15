User Guide
==========

Using `pyshotgrid` is straight forward and this guide will give teach you the basics on how
to use it under the most common scenarios.

Using `pyshotgrid` with ShotGrid Toolkit
----------------------------------------

After you made `pyshotgrid` accessible in ShotGrid Toolkit the best way to use it is to convert
any entity to a `pyshotgrid` object instance. What you need for this is:

- a shotgun_api3.Shotgun instance (which conveniently is present almost everywhere in SGTK)
- the type of the entity
- the id of the entity

These parameters will be passed to the `pyshotgrid.new_entity` method, which returns the
object you want to work with.
The method accepts 3 ways of passing arguments to it:

.. code-block:: python

    import pyshotgrid as pysg

    # These 3 lines all do the same thing: Initializing an entity instance of the Project with ID 1.
    sg_project = pysg.new_entity(sg, {'id': 1, 'type': 'Project'})
    sg_project = pysg.new_entity(sg, 1, 'Project')
    sg_project = pysg.new_entity(sg, entity_id=1, entity_type='Project')


Using `pyshotgrid` in a standalone application
----------------------------------------------

Once you installed `pyshotgrid` you can start using it throughout your project.
The best entry point usually creating a new instance of the SGSite class. This class
represents your ShotGrid site as a whole and has various functions to start navigating
through it.

.. Note::

    You should always use the `pyshotgrid.new_site` function to create a new SGSite instance.
    This ensures the plugin system works correctly and you do not get an instances of a
    wrong class at some point.

Here is an example on how to use it:

.. code-block:: python

    import pyshotgrid as pysg

    site = pysg.new_site(base_url='https://example.shotgunstudio.com',
                         script_name='Some User',
                         api_key='$ome_password')

    for project in site.projects():
        print(project)
        for shot in project.shots():
            print(shot)
            print(shot["code"].get())
