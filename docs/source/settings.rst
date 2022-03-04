Setting
=========

Some system setting options are available in SimplyFire.

.. figure:: /_static/img/settings.png
  :align: center

  Layout of the setting options

System settings can be accessed via ``Settings`` menu -> ``Settings tab``

A form will appear in the control-panel.

Application Font
------------------
Font size used in the application can be changed using
the dropdown menu in the ``Setting`` tab.

A single font size is applied to all ``tkinter`` widgets and ``matplotlib``
plot elements.
The font size of the menubar and window title cannot be changed.


Config Auto-save/load
-----------------------
User preferences can be autosaved/loaded so that the settings are
carried over to the next session.
This section controls the autosave/load behavior.

Automatically load configurations at the beginning of the next session
  Turning on the checkbox ensures that next time SimplyFire is started,
  the software attempts to load the user-preferences
  instead of the default settings.
  The location of the user-preference data is defined in the ``Data directory``
  option.

Automatically save configurations at the end of this session
  Turning on the checkbox ensures that SimplyFire attempts to save user
  preferences when the software goes through the shutoff sequence.
  The save procedures are only applied when the software is exited by normal
  means (clicking the :guilabel:`X`) and not by other means (i.e. End Task
  by Task Manager in Windows).
  The location of the user-preference data is defined in the ``Data directory``
  option.

Save log at the end of this session
  If the checkbox is marked, SimplyFire automatically saves the text in the
  **log-display** as a text file.
  The location of the user-preference data is defined in the ``Data directory``
  option.

Data directory
  Defines the directory where SimplyFire should look for various configuration
  files and save the log files (if the option is turned on).

  User preferences are saved in ``{datadirectory}/user_config.yaml``.

  The list of active plugins are saved in ``{datadirectory}/active_plugins.yaml``.

  Log files are saved in ``{datadirectory}/log`` directory.

  At software startup, SimplyFire will look for ``{datadirectory}/plugins``
  directory.
  If such a directory exists, plugin source codes will be loaded
  from this directory.
  If no such directory exists, the software defaults to the system
  plugins folder ``{simplyfire_directory}/plugins`` to look for plugin source
  code.

  Using a non-default directory allows for easy customization of the
  plugins without altering the original source code.

Save button
  Writes the current user-preferences.

Save As... button
  Saves the current user-preferences (but not the list of active-plugins)
  to a specified file path.
  Use this feature to backup a set of parameters.

Load button
  Loads the user-preferences from a file.

Default button
  Sets the autosave/load parameters to default values

Misc
-----
Number of steps to store in memory for undo
  Specify the number of operations that can be undone.
  Higher number will result in increased memory usage.

Window size
-------------
Specify the window parameters here

Window width (px)
  Sets the software width in pixels

Window height (px)
  Sets the software height in pixels

Control panel width (px)
  Sets the width of the **control-panel** in pixels.
  This can also be adjusted by dragging the handlebar between the
  **control-panel** and the **trace-display** or the **data-panel**

Graph panel height (px)
  Sets the height of the **trace-display** in pixels.
  This can also be adjusted by dragging the handlebar between
  the **trace-display** and the **data-panel**.
