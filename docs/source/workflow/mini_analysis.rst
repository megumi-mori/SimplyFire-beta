Mini analysis
==============
Overview
---------
Goal:
  Identify, annotate, and analyze spontaneous mini synaptic events
  (mEPSP, mEPSC, mEJP, mEJC)
  in the recording

Output:
  * Visual markers for individual minis
  * Exportable table of mini data (csv)
  * Data stored for future use
  * Summary

Plugins used:
  * Navigation (optional)
  * :doc:`../plugin_gui/process` (optional)
  * :doc:`../plugin_gui/mini_analysis`

Set up
---------

:ref:`open-recording` from ``file`` menu -> ``Open recording`` or ``Alt+o``.
Set the view mode to ``continuous`` by ``View`` menu -> ``continuous``
Select the channel to analyze in the channel dropdown menu.

Open plugins to use by ``Plug-ins`` menu -> select the desired plugin names.
Plugins typically have user-input forms that appear in the **control-panel**
as individual tabs.

Use the :ref:`navigation-tools` located around the plot to adjust
the x- and y-axes.

Alternatively, use the ``Navigation`` plugin to set the desired x- and y-axes
limits.


Filtering (optional)
^^^^^^^^^^^^^^^^^^^^^

If noise is high in the raw recording data, a filter may be applied.

The ``Process Recording`` plugin offers 'Lowpass Boxcar' and 'Lowpass Bessel'
filtering. Under the ``Filtering`` section, select the desired filtering
algorithm and enter the required parameters.
Save the filtered recording data by ``file`` menu -> ``Save recording data as``.

.. Caution::
  ``.abf`` files cannot be overwritten by SimplyFire.
  Filtered data should be stored as new files.


Alternatively, a filter may be applied outside of the SimplyFire environment.
Ensure that the filtered data is saved in ``.abf`` format.
Open the filtered recording using SimplyFire.

Analysis
------------------------------

Analysis is performed by :doc:`../plugin_gui/mini_analysis`.

The :doc:`../plugin_gui/mini_analysis` uses several parameters to
analyze minis.
The basic parameters are described here. For more information on all the
parameters that can be adjusted, see the :doc:`../plugin_gui/mini_analysis` page.

Parameters
^^^^^^^^^^^^^

Direction
  Indicates the expected sign of the minis.
  Typically, the direction is positive for potential and negative for current
  recordings.

Search radius in % of the visible x-axis (Manual)
  Used for manual mini analysis. Indicates the x-axis radius that is considered
  for analysis when the mouse is clicked. The radius is represented as a percentage
  of the total x-axis.
  In general, the lower number in this parameter, the higher the precision
  of the mouse-click.

Search window in ms (Auto)
  Used for automated mini analysis.
  Indicates the window of x-axis that is considered at a time.
  The window traverses from left to right, sampling the specified window at a
  time.
  In general, the lower number in this parameter, the fewer minis are skipped
  but also the slower the analysis.


  .. Caution::

    The x-axis window considered for each mini analysis must be larger than
    at least of 20 data points worth of x-axis range
    (i.e. for a 10kHz recording, the window must be larger
    than 2ms)
    Ideally, each mini analysis covers at least the approximate width of a
    single mini event.

Minimum amplitude (absolute value)
  Located under ``Filtering parameters``.
  Specify the minimum amplitude required for a mini.
  Setting this to 0 (without other filtering parameters) will result in
  most noise being annotated as a mini.



Automated analysis
^^^^^^^^^^^^^^^^^^^

Two automated analysis modes are available:
``Find all`` searches through the entire trace.
``Find in window`` searches the visible x-axis.

All discovered minis will be annotated on the plot, and the details
should appear in the **data-panel** located below the plot.

.. Caution::
  Find in window only uses the x-axis to exclude parts of the trace from analysis.
  Parts of the y-axis that are out of view may still be included in the analysis.

Manual analysis
^^^^^^^^^^^^^^^^

Navigate through the trace and click on the plot near the desired mini events.

.. Caution::
  Ensure that the **pan/zoom** and **rect to zoom** options are turned off
  in the ``matplotlib`` toolbar.
  The mouse should have the default cursor shape.

If the software detects a mini near the clicked location, it will annotate the
event on the plot.
Details of the minis will be added to the table below the plot
as new minis are discovered.

Delete minis
^^^^^^^^^^^^^

Discovered minis can be discarded using several methods.

Delete buttons
  ``Delete all`` button clears all minis found within the channel.

  ``Delete in window`` button clears data for minis found within
  the visible x-axis.

  .. Caution::
    Delete in window only uses the x-axis to select minis to discard.
    Minis that are out of the visible y-axis may still be discarded if it
    lands within the visible x-axis boundaries.

Select minis on the plot
  Clicking on the peak marker for a mini highlights it.
  Clicking on the peak marker while holding the ``Shift`` key highlights
  multiple peaks.
  Alternatively, ``left-click`` + drag to highlight minis found
  within the rectangle.
  Use the ``Escape``/``q`` key to remove the highlights.
  Use ``Ctrl+a`` to select all minis.

  Hitting the ``Delete``/``Backspace``/``e`` key deletes the data for the mini.

Select minis from the table
  Selecting entries in the **data-panel** highlights the corresponding
  mini markers on the plot.
  Press ``Shift`` and ``left-click`` to select a range of entries
  or press ``Ctrl`` and select multiple entries.
  Use ``Ctrl+a`` to select all entries.
  Use the ``Escape``/``q`` key to remove all the highlights.


  Hitting the ``Delete``/``Backspace``/``e`` key deletes all highlighted minis.

Output
-----------

Details for all minis discovered appear in the **data-panel** located below
the plot area. The panel should have a tab labeled 'Mini'.

Mini analysis calculates/stores the following properties of each mini
in the **data-panel**:

* peak time
* amplitude (signed)
* decay constant (tau)
* rise time (0-100)
* halfwidth
* baseline value
* channel number
* standard deviation of the baseline noise
* direction of the mini (-1 or 1)
* whether or not the mini is a compound mini

Each numerical column can be sorted by clicking on the column header.

Columns can be hidden or shown by toggling the checkboxes located at the
bottom of the plugin's control-panel.

Export the data
^^^^^^^^^^^^^^^^

Selected entries in the datapanel can be copied onto the
clipboard.
Data can be copied by ``Ctrl+c`` key stroke
or ``right-click`` on the **data-panel** -> ``Copy selected``.

The copied data can be pasted into Excel or other programs of choice.

The **data-panel** can also be exported to a **comma separated value (CSV)** format
by ``file`` menu -> ``Mini Analysis`` -> ``Export data table``. All data visible
in the **data-panel** are stored in the exported file.

Save the mini data
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The annotations and details for the discovered minis can be stored in a
format that can be
opened by SimplyFire later.

Go to ``file`` menu -> ``Mini Analysis`` -> ``Save minis as...`` and follow
the file save prompt.

The default extension for the mini data is ``.mini``.
The files can also be saved as ``.csv`` files and opened in other programs.
Mini data saved this way contains more details than data exported from
the **data-panel**.

Open previously analyzed minis
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Previously analyzed minis can be opened by
``file`` menu -> ``Mini Analysis`` -> ``Open mini file``.
Doing so will discard any changes in the unsaved mini data.

Summarize the data
^^^^^^^^^^^^^^^^^^^^^^

A summary of the discovered minis can be added to the  **results-display**.
The **results-display** is found in the ``results`` tab under the plot.

``Right-click`` on the **data-panel** -> ``Report all`` or ``Report selected``
or press the ``Report stats`` on the **control-panel**
to calculate the averages and standard deviations of numerical properties of minis.
Additionally, the frequency of the minis between the first and last mini
is calculated.

The result can be found in the **results-display**.
