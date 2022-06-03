# `pysg`
[![pypi](https://img.shields.io/pypi/v/pysg.svg)](https://pypi.python.org/pypi/pysg)
[![docs](https://readthedocs.org/projects/pysg/badge/?version=latest)](https://pysg.readthedocs.io/en/latest/?version=latest)

A pythonic way to talk to Autodesk ShotGrid.

* Free software: MIT license
* Documentation: https://pysg.readthedocs.io.

## Features

An entity in ShotGrid is represented by an instance of the `ShotGridEntity` class.
If you want to query a field from that instance you can do so via dictionary style:

```python
>>> import shotgun_api3
>>> import pysg
>>> sg = shotgun_api3.Shotgun(
... base_url = 'https://test.shotgunstudio.com',
... script_name = 'Some User',
... api_key = '$ome_password')
>>> sg_project = pysg.ShotGridEntity(sg, "Project", 1)
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
* Upload/Download to/from a field
  ```python
  sg_version.upload('sg_uploaded_movie', '/path/to/movie.mov')
  sg_version.download('sg_uploaded_movie', '/path/to/download/to/')
  ```
* Get the URL of the entity
  ```python
  # Get the URL directly
  sg_project.url
  ```

The rules is: All fields of an entity need to be accessed via dict notation (eg. `sg_project['code']`)
              and all "special" functionality is accessed via instance methods (eg. `sg_version.download('sg_movie', '/path/to/somewhere')`).


## Is it faster than `shotgun_api3`?
No, and since it is build on top of `shotgun_api3`, it never will be.
`pysg` is syntactic sugar that hopefully enables you to develop better and faster. :)

## Credits

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
