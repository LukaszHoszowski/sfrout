.. _api:

Here you can find exact details regarding app's internals.

Main Interface
==============

This is the entry point ot the application.

.. _run:

.. autofunction:: main.run

.. _cli:

.. click:: app.cli:cli
   :prog: cli
   :nested: full

Components
==========

.. _components:

Config
------

.. automodule:: components.config
    :members:
    :private-members:

Connectors
----------

.. automodule:: components.connectors
    :members:
    :private-members:

Containers
----------

.. automodule:: components.containers
    :members:
    :private-members:

Handlers
--------

.. automodule:: components.handlers
    :members:
    :private-members:

Excpetions
----------
.. automodule:: components.exceptions
    :members:
    :private-members:
