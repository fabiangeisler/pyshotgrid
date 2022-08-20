.. highlight:: shell

============
Installation
============


Stable release
--------------

To install pyshotgrid, run this command in your terminal:

.. code-block:: console

    $ pip install git+https://github.com/shotgunsoftware/python-api.git@v3.3.3
    $ pip install pyshotgrid

You need to install `shotgun_api3` as a separate step, in case you want to use `pyshotgrid` in
a standalone application.
This is the preferred method to install pyshotgrid, as it will always install the most recent stable release.


Use pyshotgrid with ShotGrid Toolkit
------------------------------------

There are a few ways you can use `pyshotgrid` with ShotGrid Toolkit (SGTK).
The most straight forward approach would be use it in the `tank_init.py`.

Here is what you have to do:

1. Download pyshotgrid

2. Put it in a central location where everyone can access it

3. Add the path to the `sys.path` in the `tank_init.py`.

4. You are done. :) You are now able to use `pyshotgird` throughout your SGTK setup.

   .. note::

      There is no need to install the shotgun_api3 since that is already shipped with SGTK.
