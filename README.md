# `pyshotgrid`
[![pypi](https://img.shields.io/pypi/v/pyshotgrid.svg)](https://pypi.python.org/pypi/pyshotgrid)
[![docs](https://readthedocs.org/projects/pyshotgrid/badge/?version=latest)](https://pyshotgrid.readthedocs.io/en/latest/?version=latest)

An object oriented python library for Autodesk ShotGrid.

For the Autodesk Maya guys: This aims to be what `pymel` is to `maya.cmds`.

* Free software: MIT license
* Documentation: https://pyshotgrid.readthedocs.io.

## Features

An entity in Shotgun is represented by an instance of the `ShotGridEntity` class.
If you want to query a field from that instance you can do so via dictionary style
Or dot notation:

```python
>>> import shotgun_api3
>>> import pyshotgrid as pysg
>>> sg = shotgun_api3.Shotgun(
... base_url='https://test.shotgunstudio.com',
... script_name='Unittest User',
... api_key='$ome_password')
>>> sg_project = pysg.ShotGridEntity(sg, "Project", 1)
>>> sg_project.code
"Test Project"
>>> sg_project["code"]
"Test Project"
```

You can think of a ShotgridEntity as a dictionary on steroids.
It has all the functionality of a regular dict plus a few extra functions.
So for example you can :
* iterate over all fields
  ```python
  for field, value in sg_project.items():
       print(field, value)
  ```
* Use regular dict functionality
  ```python
  sg_project.keys()
  sg_project.values()
  sg_project.get("code")
  len(sg_project)
  ```
* Update fields in ShotGrid
  ```python
  sg_project["code"] = "foobar"
  ```
* Convert it to a regular dict
  ```python
  dict(sg_project)
  ```

## Is it faster than `shotgun_api3`?
No, and since it is build on top of shotgun_api3, it never will be.
`pyshotgrid` is syntactic sugar that hopefully enables you to develop better and faster. :)

## Credits

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
