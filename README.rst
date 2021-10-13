==========
pyshotgrid
==========


.. image:: https://img.shields.io/pypi/v/pyshotgrid.svg
        :target: https://pypi.python.org/pypi/pyshotgrid

.. image:: https://readthedocs.org/projects/pyshotgrid/badge/?version=latest
        :target: https://pyshotgrid.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status


An object oriented python library for Autodesk ShotGrid.

For the Autodesk Maya guys: This aims to be what `pymel` is to `maya.cmds`.

* Free software: MIT license
* Documentation: https://pyshotgrid.readthedocs.io.

Is it faster than `shotgun_api3`?
---------------------------------
No, and since it is build on top of shotgun_api3, it never will be.
The goal is to make the syntactic sugar faster to develop. :)

Features
--------

* An entity in Shotgun is represented by an instance of the `ShotGridEntity` class.
  If you want to query a field from that instance you can do so via dictionary style
  Or dot notation::

      >>> import pyshotgrid as pysg
      >>> sg_project = pysg.ShotGridEntity("Project", 1)
      >>> sg_project.code
      "Test Project"
      >>> sg_project["code"]
      "Test Project"

* You can think of a ShotgridEntity as a dictionary on steroids.
  It has all the functionality of a regular dict plus a few extra functions.
  So for example you can :
  * iterate over all fields::

        for field, value in sg_project.items():
             print(field, value)

  * Use regular dict functionality::

        sg_project.keys()
        sg_project.values()
        sg_project.get("code")
        len(sg_project)

  * Update fields in ShotGrid::

        sg_project["code"] = "foobar"

  * Convert it to a regular dict::

        dict(sg_project)


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
