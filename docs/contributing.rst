.. highlight:: shell

============
Contributing
============

Contributions are welcome, and they are greatly appreciated! Every little bit
helps, and credit will always be given.

You can contribute in many ways:

Types of Contributions
----------------------

Report Bugs
~~~~~~~~~~~

If you are sure that you found a bug feel free to open an issue at https://github.com/fabiangeisler/pyshotgrid/issues.
In any other case please open a discussion at https://github.com/fabiangeisler/pyshotgrid/discussions.

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

Fix Bugs
~~~~~~~~

Look through the GitHub issues for bugs. Anything tagged with "bug" and "help
wanted" is open to whoever wants to implement it.

Implement Features
~~~~~~~~~~~~~~~~~~

Look through the GitHub issues for features. Anything tagged with "enhancement"
and "help wanted" is open to whoever wants to implement it.

Write Documentation
~~~~~~~~~~~~~~~~~~~

pyshotgrid could always use more documentation, whether as part of the
official pyshotgrid docs, in docstrings, or even on the web in blog posts,
articles, and such.

Submit Feedback
~~~~~~~~~~~~~~~

The best way to send feedback is to open a discussion at https://github.com/fabiangeisler/pyshotgrid/discussions.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

Get Started!
------------

Ready to contribute? Here's how to set up `pyshotgrid` for local development.

1. Fork the `pyshotgrid` repo on GitHub.
2. Clone your fork locally::

    $ git clone git@github.com:your_name_here/pyshotgrid.git

3. Setup your virtual environment with Python 3.7::

    $ python -m venv venv
    $ source venv/bin/activate
    $ python -m pip install -U pip
    $ python -m pip install -r requirements.txt
    $ python -m pip install -e .

4. Create a branch for local development::

    $ git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

5. When you're done making changes, check that your changes pass flake8 and the
   tests by running tox::

    $ tox

   To run the tests against other Python versions you need to have them installed on
   your machine.

6. Commit your changes and push your branch to GitHub::

    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature

7. Submit a pull request through the GitHub website.

Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring, and update the documentation
   where applicable.
3. The pull request should work for Python 2.7, 3.7, 3.8 and 3.9. Check
   the test-actions attached to your pull request
   and make sure that all or them pass for the supported Python versions.

Tips
----

To run a subset of tests::


    $ python -m unittest tests.test_pyshotgrid

Deploying
---------

A reminder for the maintainers on how to deploy.
Make sure all your changes are committed.
Then run::

$ bump2version patch # possible: major / minor / patch
$ git push
$ git push --tags
