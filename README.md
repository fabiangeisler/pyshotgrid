# `pyshotgrid`
[![pypi](https://img.shields.io/pypi/v/pyshotgrid.svg)](https://pypi.python.org/pypi/pyshotgrid)
[![docs](https://readthedocs.org/projects/pyshotgrid/badge/?version=latest)](https://pyshotgrid.readthedocs.io/en/latest/?version=latest)

A pythonic and more object oriented way to talk to Autodesk ShotGrid.

> **Warning**
> This python library is still in early development and the API is not yet stable.
> Please be cautious in a production environment.

* Free software: MIT license
* Documentation: https://pyshotgrid.readthedocs.io.

## Usage

The `pyshotgrid.SGSite` class provides a common entry point
to talk to your ShotGrid site. For example to list all shots
From all projects you can do this:

```python
import pyshotgrid as pysg
site = pysg.SGSite.from_credentials(
    base_url = 'https://example.shotgunstudio.com',
    script_name = 'Some User',
    api_key = '$ome_password')
for project in site.projects():
    print(project)
    for shot in project.shots():
        print(shot)
```

## Features

A SGEntity instance represents exactly one entity and any operation on it is reflected to ShotGrid.
So for example you can :

* Get fields from ShotGrid
  ```python
  print(sg_project["code"])  # "foobar"
  print(sg_project.get(["code", "tank_name"]))  # {"code": "foobar", "tank_name": "fb"}
  ```
* Values are automatically converted to `pyshotgrid` objects which makes it
  possible to chain queries together.
  ```python
  print(sg_playlist["versions"][0]["code"])  # Name of the first Version in the Playlist.
  ```
* Update fields in ShotGrid
  ```python
  sg_project["code"] = "foobar"
  sg_project.set({"code": "foobar", "tank_name": "fb"})
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
* Convert it to a regular dict, to use it in the regular `shotgun_api3`.
  ```python
  sg_project.to_dict()  # {"type": "Project", "id": 1}
  ```
* iterate over all fields
  ```python
  for field, value in sg_project.all_fields().items():
       print(field, value)
  ```
The rules is: All fields of an entity are accessed via dict notation (eg. `sg_project['code']`)
              and all "special" functionality is accessed via instance methods (eg. `sg_version.download('sg_movie', '/path/to/somewhere')`).

## How it works

Behind the scenes we have one `SGEntity` class which is the base class for all
other classes. It represents a single entity of a ShotGrid site and only
stores 3 values:
 - The shotgun_api3.Shotgun instance that is used to get and set all the information from.
 - The ShotGrid entity type
 - The ShotGrid entity ID

All functionality of the `SGEntity` class is based on these three values.
There are some "special" classes that inherit from `SGEntity` to add some
common functionality to common entities in ShotGrid. For example the `SGProject`
class adds a `shots()` function which gives you a list of shots from that project.
To ensure that you are always using the right class you should use the `pyshotgrid.convert()`
function which will return the right instance for you.

## FAQ

### Is it faster than `shotgun_api3`?
No, and since it is build on top of `shotgun_api3`, it never will be.
`pyshotgrid` is syntactic sugar that hopefully enables you to develop better and faster. :)

### Is `pyshotgrid` replacing `shotgun_api3`?
No, quite the opposite. It is meant to be used in conjunction with `shotgun_api3` and
improve handling and writing code with it. Its main goal is to make it easier to write
code for common scenarios and leave the special cases for the `shotgun_api3`. That said
It is possible totally possible to write pyshotgrid code without using `shotgun_api3`.

### I have some custom entity setup in Shotgrid. Can this be reflected in `pyshotgrid`?
By default pyshotgrid returns any entity as SGEntity to provide
A minimum of functionality in all cases. But you can write your own class
that inherits from `SGEntity` and register that to `pyshotgrid`. After that
whenever pyshotgrid encounters your custom entity it will
return your custom implementation. You can even overwrite
default classes that ship with `pyshotgrid`.

### Is this an official project from Autodesk?
No, just a brainchild from me, https://github.com/fabiangeisler.
I am a Pipeline Developer based in Berlin.
Feel free to follow me on GitHub. :)

## Credits

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
