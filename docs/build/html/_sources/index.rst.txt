SFrout - Sales Force Report Downloader
======================================

.. Release v\ |version|. (:ref:`Installation <install>`)

.. image:: https://static.pepy.tech/badge/sfrout
    :target: https://static.pepy.tech/badge/sfrout
    :alt: SFrout Downloads
    
.. image:: https://img.shields.io/pypi/l/sfrout.svg
    :target: https://pypi.org/project/sfrout/
    :alt: License Badge

.. image:: https://img.shields.io/pypi/wheel/sfrout.svg
    :target: https://pypi.org/project/sfrout/
    :alt: Wheel Support Badge

.. image:: https://img.shields.io/pypi/pyversions/sfrout.svg
    :target: https://pypi.org/project/sfrout/
    :alt: Python Version Support Badge

**SFrout** is a scalable, asynchronous SalesForce report downloader for SAML/SSO clients. 


What problem does this app solve?
---------------------------------

In some organizations users are allowed to use only user interface with SSO authentication.
No API, Security Tokens and other alternative connectors. This app automate authentication 
process, allow users to downloaded multiple SFDC reports, with custom parameteres, in 
asynchronous fashion. 


Main features:
--------------

- download single or multiple ``SFDC`` reports
- asynchronous requestes
- threaded IO processes
- queued transport
- fail safe, download the report or die trying
- dual interface, ``importable package`` / ``CLI``
- logging to stdout / file
- summary report in ``csv`` and ``console``
- dual report input format, ``csv`` / ``list[dict]`` 
- progress displayed as ``progress bar`` or ``console output``
- customizable number of workers


The User Guide
--------------

If you plane to use **SFrout** this place is for you.

.. toctree::
   :maxdepth: 1

   user/install
   user/quickstart
   user/advanced
   user/how


The API Documentation
---------------------

Let's have a look under the hood.

.. toctree::
   :maxdepth: 3

   api


The Components Documentation
----------------------------

Let's go even deeper.

.. toctree::
   :maxdepth: 3

   internals


Index
-----

* :ref:`genindex`