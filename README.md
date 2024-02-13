<p align="center">
  <img src="https://github.com/fabiangeisler/pyshotgrid/blob/main/icons/pysg_logo.png?raw=true" />
</p>

[![VFX Platform](https://img.shields.io/badge/vfxplatform-2024%20%7C%202023%20%7C%202022-white.svg)](http://www.vfxplatform.com/)
[![pypi](https://img.shields.io/pypi/v/pyshotgrid.svg)](https://pypi.python.org/pypi/pyshotgrid)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/pyshotgrid.svg)](https://pypi.python.org/pypi/pyshotgrid/)
[![Tests](https://github.com/fabiangeisler/pyshotgrid/actions/workflows/Tests.yml/badge.svg)](https://github.com/fabiangeisler/pyshotgrid/actions/workflows/Tests.yml)
[![coverage](https://img.shields.io/badge/%20coverage-99%25-%231674b1?style=flat&color=darkgreen)](https://github.com/fabiangeisler/pyshotgrid/actions/workflows/Tests.yml)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)

`pyshotgrid` is a python package that gives you a pythonic and
object oriented way to talk to [Autodesk ShotGrid](https://www.autodesk.com/products/shotgrid/overview).

# Quickstart

Install `pyshotgrid` via pip:

```shell
pip install pyshotgrid
```

You are now ready to use it in your project (For other installation methods see the
[Installation](https://fabiangeisler.github.io/pyshotgrid/installation.html) section in the documentation)!
Here is a quick example to list the "code" (aka. "name") of all shots from all projects:

```python
import pyshotgrid as pysg

site = pysg.new_site(base_url='https://example.shotgunstudio.com',
                     script_name='Some User',
                     api_key='$ome_password')

for project in site.projects():
    print(project["name"].get())
    for shot in project.shots():
        print(shot["code"].get())
```

# Features

In `pyshotgrid` you are working with [SGEntity][SGEntity] instances which each represent exactly one entity
in ShotGrid. Any operation on it is reflected to ShotGrid.
So for example you can :

* Get entity fields in ShotGrid
  ```python
  # Get the value of a field ...
  print(sg_project["name"].get())  # "foobar"
  # ... or get multiple fields at once.
  print(sg_project.get(["name", "tank_name"]))  # {"name": "foobar", "tank_name": "fb"}
  ```
* Update entity fields in ShotGrid
  ```python
  # Set the value of a field ...
  sg_project["name"].set("foobar")
  # ... or set multiple fields at once.
  sg_project.set({"name": "foobar", "tank_name": "fb"})
  ```
* Values are automatically converted to `pyshotgrid` objects which makes it
  possible to chain queries together.
  ```python
  # Name of the first Version in a Playlist.
  print(sg_playlist["versions"].get()[0]["code"].get())
  ```
* Get information about a field
  ```python
  print(sg_project["name"].data_type)     # "text"
  print(sg_project["name"].description)   # "The name of the project."
  print(sg_project["name"].display_name)  # "Project Name"
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
* Convert it to a regular dict, to use it in Autodesk [shotgun_api3][shotgun_api3].
  ```python
  sg_project.to_dict()  # {"type": "Project", "id": 1}
  ```
* Iterate over all fields
  ```python
  # Iterate over the fields directly to get some information about them...
  for field, value in sg_project.fields().items():
       print(field.display_name)
  # ... or iterate over the fields and values at the same time.
  for field_name, value in sg_project.all_field_values().items():
       print(field_name, value)
  ```
* Do you keep forgetting which field is the "name" of an entity? (was it "code" or "name"?)
  Just use the "SGEntity.name" property:
  ```python
  sg_project.name  # returns the "name" field.    Same as:  sg_project["name"]
  sg_shot.name     # returns the "code" field.    Same as:  sg_shot["code"]
  sg_task.name     # returns the "content" field. Same as:  sg_task["content"]
  ```

* It is possible to inherit from [SGEntity][SGEntity] and create implementations for specific
  entity types. `pyshotgrid` ships with a few common entities by default. For example
  the implementation for the `Project` entity ([SGProject][SGProject]) gives you additional functions
  to query shots, assets or publishes:
  ```python
  sg_project.shots()
  sg_project.assets()
  sg_project.publishes()
  ```
  Checkout the [overview of all the default entities][Overview default entities] and the
  [API documentation][API sg_default_entities] for all the extra functionality!
  As an additional bonus: You can customize and extend all these classes to your hearts content.
  Have a look at [How to add custom entities][How to add custom entities] in the docs.

# FAQ

## Is it faster than [shotgun_api3][shotgun_api3]?
No, and since it is build on top of [shotgun_api3][shotgun_api3], it never will be.
`pyshotgrid` is syntactic sugar that hopefully enables you to develop better and faster. :)

## Is `pyshotgrid` replacing [shotgun_api3][shotgun_api3]?
No, quite the opposite. It is meant to be used in conjunction with [shotgun_api3][shotgun_api3] and
improve handling and writing code with it. Its main goal is to make it easier to write
code for common scenarios and leave the special cases for [shotgun_api3][shotgun_api3]. That said,
it is totally possible to write `pyshotgrid` code without using [shotgun_api3][shotgun_api3].

## I have some custom entity setup in ShotGrid. Can this be reflected in `pyshotgrid`?
Yes, it can! By default `pyshotgrid` returns any entity as [SGEntity][SGEntity] to provide
a minimum of functionality in all cases. However you can write your own class
that inherits from [SGEntity][SGEntity] and register that to `pyshotgrid`. After that,
`pyshotgrid` will use your custom entity whenever you ask for it. With this method
you can even overwrite default classes that ship with `pyshotgrid`.

## Why is does `pyshotgrid` not support Python 3.7? [shotgun_api3][shotgun_api3] has support for it.
A couple of reasons:
- [Python 3.7 reached EOL](https://devguide.python.org/versions/) and is no longer maintained.
- Python 3.7 is soon off the [VFX Reference Platform](https://vfxplatform.com/).
- The hidden goal of this project is to create a python library that uses the latest
  innovations in the Python world.
  In a nutshell I want to create the simplest setup that gives you:
  - automatic publishing to PyPI
  - automatic testing with tox, pytest and coverage
  - automatic [Sphinx](https://www.sphinx-doc.org/en/master/) documentation
  - [mypy](https://mypy-lang.org/) type hints
  - [ruff](https://github.com/astral-sh/ruff) linting
  - [black](https://github.com/psf/black) code formatting (actually done by `ruff format`)
  - [pre-commit](https://github.com/pre-commit/pre-commit) checks
  - [invoke](https://www.pyinvoke.org/) setup for common tasks in the repository
  - streamlined commit messages and changelog with [commitizen](https://github.com/commitizen-tools/commitizen)

  A good chunk of these tools do not support Python 3.7 anymore and I do not have the time to
  keep up the compatibility.

## Is this an official project from Autodesk?
No, just a brainchild from me, [Fabian Geisler](https://github.com/fabiangeisler).
I am a Pipeline Developer based in Berlin.
Feel free to follow me on GitHub. :)

# Credits

This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and
the [audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage) project template
(but was heavily modified in the meantime).

[SGEntity]: https://fabiangeisler.github.io/pyshotgrid/modules/core.html#pyshotgrid.core.SGEntity
[SGProject]: https://fabiangeisler.github.io/pyshotgrid/modules/sg_default_entities.html#pyshotgrid.sg_default_entities.SGProject
[Overview default entities]: https://fabiangeisler.github.io/pyshotgrid/default_entities_overview.html
[API sg_default_entities]: https://fabiangeisler.github.io/pyshotgrid/modules/sg_default_entities.html
[How to add custom entities]: https://fabiangeisler.github.io/pyshotgrid/how_to_add_custom_entities.html
[shotgun_api3]: https://github.com/shotgunsoftware/python-api
