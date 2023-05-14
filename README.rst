Introduction
============


.. image:: https://readthedocs.org/projects/circuitpython-tmp117/badge/?version=latest
    :target: https://circuitpython-tmp117.readthedocs.io/
    :alt: Documentation Status


.. image:: https://img.shields.io/pypi/v/circuitpython-tmp117.svg
    :alt: latest version on PyPI
    :target: https://pypi.python.org/pypi/circuitpython-tmp117

.. image:: https://static.pepy.tech/personalized-badge/circuitpython-tmp117?period=total&units=international_system&left_color=grey&right_color=blue&left_text=Pypi%20Downloads
    :alt: Total PyPI downloads
    :target: https://pepy.tech/project/circuitpython-tmp117

.. image:: https://github.com/jposada202020/CircuitPython_TMP117/workflows/Build%20CI/badge.svg
    :target: https://github.com/jposada202020/CircuitPython_TMP117/actions
    :alt: Build Status

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
    :alt: Code Style: Black


CircuitPython TMP117 Temperature Sensor Low Memory driver. This is refactor to work with a QT Py M0.
See issue https://github.com/adafruit/Adafruit_CircuitPython_TMP117/issues/11

The work here was covered under PR#15
on the Adafruit_TMP117 Library https://github.com/adafruit/Adafruit_CircuitPython_TMP117/pull/15

There were small changes after the PR, those are included here too.





Dependencies
=============
This driver depends on:

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_
* `Bus Device <https://github.com/adafruit/Adafruit_CircuitPython_BusDevice>`_
* `Register <https://github.com/adafruit/Adafruit_CircuitPython_Register>`_

Please ensure all dependencies are available on the CircuitPython filesystem.


Installing from PyPI
=====================

On supported GNU/Linux systems like the Raspberry Pi, you can install the driver locally `from
PyPI <https://pypi.org/project/circuitpython-tmp117/>`_.
To install for current user:

.. code-block:: shell

    pip3 install circuitpython-tmp117

To install system-wide (this may be required in some cases):

.. code-block:: shell

    sudo pip3 install circuitpython-tmp117

To install in a virtual environment in your current project:

.. code-block:: shell

    mkdir project-name && cd project-name
    python3 -m venv .venv
    source .env/bin/activate
    pip3 install circuitpython-tmp117


Usage Example
=============

Take a look at the examples directory
