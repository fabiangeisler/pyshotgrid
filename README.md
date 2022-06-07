# `pyshotgrid`
[![pypi](https://img.shields.io/pypi/v/pyshotgrid.svg)](https://pypi.python.org/pypi/pyshotgrid)
[![docs](https://readthedocs.org/projects/pyshotgrid/badge/?version=latest)](https://pyshotgrid.readthedocs.io/en/latest/?version=latest)

A pythonic way to talk to Autodesk ShotGrid.

* Free software: MIT license
* Documentation: https://pyshotgrid.readthedocs.io.

## Features

An entity in ShotGrid is represented by an instance of the `ShotGridEntity` class.
If you want to query a field from that instance you can do so via dictionary style:

```python
>>> import shotgun_api3
>>> import pyshotgrid
>>> sg = shotgun_api3.Shotgun(
... base_url = 'https://example.shotgunstudio.com',
... script_name = 'Some User',
... api_key = '$ome_password')
>>> sg_project = pyshotgrid.ShotGridEntity(sg, "Project", 1)
>>> sg_project["code"]
"Test Project"
```

A ShotGridEntity instance represents exactly one entity and
any operation on it is reflected to ShotGrid.
So for example you can :

* Get fields from ShotGrid
  ```python
  print(sg_project["code"])  # "foobar"
  print(sg_project.get(["code", "tank_name"]))  # {"code":"foobar", "tank_name": "fb"}
  ```
* Update fields in ShotGrid
  ```python
  sg_project["code"] = "foobar"
  sg_project.set({"code":"foobar", "tank_name": "fb"})
  ```
* Upload/Download to/from a field
  ```python
  sg_version.upload('sg_uploaded_movie', '/path/to/movie.mov')
  sg_version.download('sg_uploaded_movie', '/path/to/download/to/')
  ```
* Get the URL of the entity
  ```python
  print(sg_project.url)  # https://example.shotgunstudio.com/detail/Project/1
  ```
* Convert it to a regular dict which can be used in the regular shotgun_api3
  ```python
  sg_project.to_dict()  # {"type": "Project", "id": 1}
  ```
* iterate over all fields
  ```python
  for field, value in sg_project.all_fields().items():
       print(field, value)
  ```
The rules is: All fields of an entity need to be accessed via dict notation (eg. `sg_project['code']`)
              and all "special" functionality is accessed via instance methods (eg. `sg_version.download('sg_movie', '/path/to/somewhere')`).


## Is it faster than `shotgun_api3`?
No, and since it is build on top of `shotgun_api3`, it never will be.
`pyshotgrid` is syntactic sugar that hopefully enables you to develop better and faster. :)

## Credits

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
