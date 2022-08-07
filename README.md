[![pypi](https://img.shields.io/pypi/v/pyshotgrid.svg)](https://pypi.python.org/pypi/pyshotgrid)
[![Python 2.7 3.7 3.8 3.9](https://img.shields.io/badge/python-2.7%20%7C%203.7%20%7C%203.8%20%7C%203.9-blue.svg)](https://www.python.org/)
[![Tests](https://github.com/fabiangeisler/pyshotgrid/actions/workflows/Tests.yml/badge.svg)](https://github.com/fabiangeisler/pyshotgrid/actions/workflows/Tests.yml)
[![docs](https://readthedocs.org/projects/pyshotgrid/badge/?version=latest)](https://pyshotgrid.readthedocs.io/en/latest/?version=latest)

# Overview

`pyshotgrid` is a python package that gives you a pythonic and
object oriented way to talk to [Autodesk ShotGrid](https://www.autodesk.com/products/shotgrid/overview).

> **Warning**
> This python library is still in early development and the API is not yet stable.
> Please be cautious in a production environment.

* Documentation: https://pyshotgrid.readthedocs.io.

## Quickstart

Install `pyshotgrid` via pip:

```shell
pip install git+https://github.com/shotgunsoftware/python-api.git@v3.3.1
pip install pyshotgrid
```

You are now ready to use it in your project (For other installation methods see the
Installation section in the documentation)!
Here is a quick example to list the "code" (aka. "name") of all shots from all projects:

```python
import pyshotgrid as pysg

site = pysg.new_site(base_url='https://example.shotgunstudio.com',
                     script_name='Some User',
                     api_key='$ome_password')

for project in site.projects():
    print(project)
    for shot in project.shots():
        print(shot)
        print(shot["code"].get())
```

## Features

In `pyshotgrid` you are working with `SGEntity` instances which each represent exactly one entity
in ShotGrid. Any operation on it is reflected to ShotGrid.
So for example you can :

* Get fields from ShotGrid
  ```python
  # Get the value of a field ...
  print(sg_project["code"].get())  # "foobar"
  # ... or get multiple fields at once.
  print(sg_project.get(["code", "tank_name"]))  # {"code": "foobar", "tank_name": "fb"}
  ```
* Update fields in ShotGrid
  ```python
  # Set the value of a field ...
  sg_project["code"].set("foobar")
  # ... or set multiple fields at once.
  sg_project.set({"code": "foobar", "tank_name": "fb"})
  ```
* Values are automatically converted to `pyshotgrid` objects which makes it
  possible to chain queries together.
  ```python
  print(sg_playlist["versions"].get()[0]["code"].get())  # Name of the first Version in the Playlist.
  ```
* Get information about a field
  ```python
  print(sg_project["code"].data_type)
  print(sg_project["code"].description)
  print(sg_project["code"].display_name)
  ```
* Upload/Download to/from a field
  ```python
  sg_version['sg_uploaded_movie'].upload('/path/to/movie.mov')
  sg_version['sg_uploaded_movie'].download('/path/to/download/to/')
  ```
* Get the URL of the entity
  ```python
  print(sg_project.url)  # https://example.shotgunstudio.com/detail/Project/1
  ```
* Convert it to a regular dict, to use it in Autodesk's `shotgun_api3`.
  ```python
  sg_project.to_dict()  # {"type": "Project", "id": 1}
  ```
* iterate over all fields
  ```python
  # Iterate over the fields directly to get some information about them...
  for field, value in sg_project.fields().items():
       print(field.display_name)
  # ... or iterate over the fields and values at the same time.
  for field_name, value in sg_project.all_field_values().items():
       print(field_name, value)
  ```

Each SGEntity can have special functionality assigned to it. For example the
default implementation for the Project entity gives you functions to easily query shots, assets
or publishes.
  ```python
  sg_project.shots()
  sg_project.assets()
  sg_project.publishes()
  ```
Checkout the API documentation for all the extra functionality.
You can also customize the classes to fit your workflow needs.

## FAQ

### Is it faster than `shotgun_api3`?
No, and since it is build on top of `shotgun_api3`, it never will be.
`pyshotgrid` is syntactic sugar that hopefully enables you to develop better and faster. :)

### Is `pyshotgrid` replacing `shotgun_api3`?
No, quite the opposite. It is meant to be used in conjunction with `shotgun_api3` and
improve handling and writing code with it. Its main goal is to make it easier to write
code for common scenarios and leave the special cases for the `shotgun_api3`. That said,
it is possible totally possible to write `pyshotgrid` code without using `shotgun_api3`.

### I have some custom entity setup in ShotGrid. Can this be reflected in `pyshotgrid`?
Yes, it can! By default `pyshotgrid` returns any entity as `SGEntity` to provide
A minimum of functionality in all cases. But you can write your own class
that inherits from `SGEntity` and register that to `pyshotgrid`. After that
whenever pyshotgrid encounters your custom entity it will
return your custom implementation. You can even overwrite
default classes that ship with `pyshotgrid`.

### Is this an official project from Autodesk?
No, just a brainchild from me, [Fabian Geisler](https://github.com/fabiangeisler).
I am a Pipeline Developer based in Berlin.
Feel free to follow me on GitHub. :)

## Credits

This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and
the [audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage) project template
(but was heavily modified in the meantime).
