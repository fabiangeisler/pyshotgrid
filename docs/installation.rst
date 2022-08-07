.. highlight:: shell

============
Installation
============


Stable release
--------------

To install pyshotgrid, run this command in your terminal:

.. code-block:: console

    $ pip install git+https://github.com/shotgunsoftware/python-api.git@v3.3.1
    $ pip install pyshotgrid

You need to install `shotgun_api3` as a separate step, because it is not present on Pypi.
This is the preferred method to install pyshotgrid, as it will always install the most recent stable release.

If you don't have `pip`_ installed, this `Python installation guide`_ can guide
you through the process.

.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/


From sources
------------

The sources for pyshotgrid can be downloaded from the `Github repo`_.

You can either clone the public repository:

.. code-block:: console

    $ git clone git://github.com/fabiangeisler/pyshotgrid

Or download the `tarball`_:

.. code-block:: console

    $ curl -OJL https://github.com/fabiangeisler/pyshotgrid/tarball/master

Once you have a copy of the source, you can install it with:

.. code-block:: console

    $ python setup.py install


.. _Github repo: https://github.com/fabiangeisler/pyshotgrid
.. _tarball: https://github.com/fabiangeisler/pyshotgrid/tarball/master


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
