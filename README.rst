⛔️ DEPRECATED
===============

This repository is no longer supported, please consider using alternatives.

.. image:: http://unmaintained.tech/badge.svg
  :target: http://unmaintained.tech
  :alt: No Maintenance Intended



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
