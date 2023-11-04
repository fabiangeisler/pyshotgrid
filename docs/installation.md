# Installation

## Stable release

To install pyshotgrid, run this command in your terminal:

```shell
pip install pyshotgrid
```

This is the preferred method to install pyshotgrid, as it will always install the most recent stable release.

## Use pyshotgrid with ShotGrid Toolkit

There are a few ways you can use `pyshotgrid` with ShotGrid Toolkit (SGTK) and it will likely
differ from studio to studio how it should be added to the setup.
One of the most straight forward approaches would be adding `pyshotgrid` to
the `sys.path` in the `tank_init.py`.

Here is what you have to do:

1. Download pyshotgrid
   ```shell
   pip download --no-deps --dest /path/to/download/pyshotgrid pyshotgrid
   ```
2. Put it in a central location where everyone can access it
3. Add the path to the `sys.path` in the `tank_init.py`.
4. You are done. :) You are now able to use `pyshotgird` throughout your SGTK setup.
