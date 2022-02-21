
Getting Started
================
Installation
--------------

.exe Installation for Windows (simple)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Download the software zip file from the latest github repository.

`Download SimplyFire zip <https://github.com/megumi-mori/SimplyFire-beta/releases/download/v0.3.0-beta/SimplyFire0.3.0.zip>`_.

Extract the contents of the zip file.
Within the `SimplyFire` root folder, locate `SimplyFire.exe`.
Run the executable file to begin the application.

That's it!

Supported systems:

* Windows 10


Python Installation (advanced)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

SimplyFire can be installed as a Python module through PyPI.

Install SimplyFire from `TestPyPI <https://test.pypi.org/project/SimplyFire/>`_ using
`pip` as follows::

  pip install -i https://test.pypi.org/simple/ simplyfirebeta


The package will be made available on the main PyPI database in the future for stable releases.

Once installed, run SimplyFire from any directory::

  py -m simplyfire

SimplyFire is mainly a GUI-based software.
However, the algorithms for analyses can be imported as packages and used in Python scripts.

Required Packages:

SimplyFire is dependent on the following packages (with tested version numbers):

* `numpy <https://numpy.org/>`_ (>=1.21.5)
* `matplotlib <https://matplotlib.org/>`_ (>=3.5.1)
* `pandas <https://pandas.pydata.org/>`_ (>=1.3.5)
* `scipy <https://scipy.org/>`_ (>=1.7.3)
* `pyyaml <https://pyyaml.org/>`_ (>=6.0)
* `pyabf <https://swharden.com/pyabf/>`_ (>=2.3.5)

Earlier packages have not been tested, but they may still work.

Supported Systems:

The code has been developed on Windows 10.

While most of the code should work on any platform,
some of the GUI event-handling and file read/write may be system specific.

OSX and Linux testers are welcome to submit system-specific issues!

Source Code (developer)
^^^^^^^^^^^^^^^^^^^^^^^^
SimplyFire is entirely written in Python.

The source code can be found in the `GitHub repository <https://github.com/megumi-mori/SimplyFire-beta>`_

Algorithm specific to a plugin are stored as separate submodules.
These modules do not require the GUI component, and may be imported independently of the GUI application.


Supported Systems:

The code has been developed on Windows 10.

The GUI component may have system-specific code.
The analysis modules should work independently of the system environment.

System-specific issues are welcome!

Using the software
---------------------
SimplyFire can read files stored in `.abf` format
