Contributing
============

Runcrate is open source software distributed under the `Apache License, Version 2.0 <https://www.apache.org/licenses/LICENSE-2.0>`_. Contributions are welcome, but please read this guide first. Submitted contributions are assumed to be covered by section 5 of the license.


Initial setup
-------------

`Set up Git <https://docs.github.com/en/github/getting-started-with-github/set-up-git>`_ on your local machine, then `fork <https://docs.github.com/en/github/getting-started-with-github/fork-a-repo>`_ this repository on GitHub and `create a local clone of your fork <https://docs.github.com/en/github/getting-started-with-github/fork-a-repo#step-2-create-a-local-clone-of-your-fork>`_.

For instance, if your GitHub user name is ``simleo``, you can get a local clone as follows::

   $ git clone https://github.com/simleo/runcrate

You can see that the local clone is pointing to your remote fork::

   $ cd runcrate
   $ git remote -v
   origin  https://github.com/simleo/runcrate (fetch)
   origin  https://github.com/simleo/runcrate (push)

To keep a reference to the original (upstream) ro-crate repository, you can add a remote for it::

   $ git remote add upstream https://github.com/ResearchObject/runcrate
   $ git fetch upstream

This allows, among other things, to easily keep your fork synced to the upstream repository through time. For instance, to sync your ``main`` branch::

   $ git checkout master
   $ git fetch -p upstream
   $ git merge --ff-only upstream/master
   $ git push origin master

If you need help with Git and GitHub, head over to the `GitHub docs <https://docs.github.com/en/github>`_. In particular, you should be familiar with `issues and pull requests <https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests>`_.


Making a contribution
---------------------

Contributions can range from fixing a broken link or a typo in the documentation to fixing a bug or adding a new feature to the software. Ideally, contributions (unless trivial) should be related to an `open issue <https://github.com/ResearchObject/runcrate/issues>`_. If there is no existing issue or `pull request <https://github.com/ResearchObject/runcrate/pulls>`_ related to the changes you wish to make, you can open a new one.

Make your changes on a branch in your fork, then open a pull request (PR). Please take some time to summarize the proposed changes in the PR's description, especially if they're not obvious. If the PR addresses an open issue, you should `link it to the issue <https://docs.github.com/en/github/managing-your-work-on-github/linking-a-pull-request-to-an-issue>`_.

An important part of the contribution process is checking that your changes didn't break anything. We use `Tox <https://tox.readthedocs.io/en/latest/>`_ to run unit tests and other checks. You can install Tox by running::

  pip install tox

If you made changes to the code, you should run::

  tox -e lint
  tox -e test
  tox -e build

If you changed the documentation, run::

  tox -e docs

You can also perform all of the above checks at once by simply running ``tox``.


Contributing software
^^^^^^^^^^^^^^^^^^^^^

runcrate is written in `Python <https://www.python.org>`_. To isolate your development environment from the underlying system, set up a virtual environment::

  python3 -m venv venv
  source venv/bin/activate
  pip install --upgrade pip
  pip install wheel

Then install runcrate in development mode::

  pip install -e .

This allows to test any changes to the code without having to run the installation again. To quickly run tests while developing, install pytest::

  pip install pytest

Than you can run all tests with::

  pytest tests

Or just run individual tests that are relevant to your changes, e.g.::

  pytest tests/test_step_mapping.py::test_step_maps

When you're done with your work, you can deactivate the virtual
environment by typing ``deactivate`` on your shell.

For more information, see the `PyPA guide on virtual environments <https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/>`_.


Contributing documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^

Documentation is written in `reStructuredText <https://docutils.sourceforge.io/rst.html>`_ and rendered with `Sphinx <https://www.sphinx-doc.org/>`_. If you make changes to it, run ``tox -e docs`` to check that the build works. Note that this will run ``sphinx-build`` with the ``-W`` flag, which turns all warnings into errors. While making changes to the documentation, it might be more useful to get a list of all issues at once::

  tox -e docs -- -E
