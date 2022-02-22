Mini analysis
==============
Overview
---------
Goal:
  Identify and analyze spontaneous mini synaptic events (mEPSP, mEPSC, mEJP, mEJC)
  in the recording

Output:
  * Visual markers for individual minis
  * Exportable table of mini data (csv)
  * Data stored for future use

Plugins used:
  * Navigation (optional)
  * Process Recording (optional)
  * Mini Analysis

Open recording
----------------

:ref:`open-recording` and set to ``continuous`` view mode.
Select the channel to analyze.

Navigate
---------

For automated analysis, use the :ref:`navigation` to adjust
the x-axis such that only the desired range for analysis is displayed on the plot.
For manual analysis, use the :ref:`navigation` so that the minis are
visually recognizable.

Additionally, the ``Navigation`` plugin offers additional ways to easily
navigate through the recording data.

Filter
--------

If noise is high in the raw recording data, a filter may be applied.

The ``Process Recording`` plugin offers some filtering options.

Alternatively, a filter may be applied outside of the SimplyFire environment.
As long as the filtered data is stored in ``.abf`` format,
SimplyFire is able to handle the filtered data.

Set mini analysis parameters
------------------------------

The ``Mini Analysis`` plugin depends on a handful of parameters to find minis.
The basic parameters are described here. For more information on all the
parameters that can be adjusted, see the ``Mini Analysis`` plugin page.

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
-------------------

Once the desired parameters are set, click on ``Find all`` to scan through
the entire trace.
To only sample from a subset of the trace, click on ``Find in window`` to
search only the visible x-axis.

All discovered minis will be annotated on the plot, and the details
should appear in the data tab underneath the plot.

.. Caution::
  Find in window only uses the x-axis to exclude parts of the trace from analysis.
  Parts of the y-axis that are out of view may still be included in the analysis.

Manual analysis
-------------------

Navigate through the trace and click on the plot near the desired mini events.

.. Caution::
  Ensure that the **pan/zoom** and **rect to zoom** options are turned off
  in the ``matplotlib`` toolbar.
  The mouse should have the default cursor shape.

If the software detects a mini near the clicked location, it will annotate the
event on the plot.
Details of the minis will be added to the table underneath the plot
as new minis are discovered.

Delete minis
---------------

Discovered minis can be discarded using several methods.

Delete all
  Click on the ``Delete all`` button to clear all minis found within the channel.

Delete in window
  Click on the ``Delete in window`` button to clear data for minis found within
  the visible x-axis.

  .. Caution::
    Delete in window only uses the x-axis to select minis to discard.
    Minis that are out of the visible y-axis may still be discarded if it
    lands within the visible x-axis boundaries.

Single selection from plot
  Clicking on the peak marker for a mini highlights it.
  Hitting the ``Delete``/``Backspace``/``e`` key deletes the data for the mini.

Multiple selection from plot
  Left-click and dragging highlights multiple minis.
  Hitting the ``Delete``/``Backspace``/``e`` key deletes all highlighted minis.

Selection from the table
  A single or multiple entries in the table highlights the corresponding mini.
  Hitting the ``Delete``/``Backspace``/``e`` key deletes all highlighted minis.

Read the data
--------------------

Details for all minis discovered appear in the table located beneath
the plot area. The table should have a tab labeled 'Mini'.

Mini analysis calculates the following properties of each mini:

* amplitude
* decay constant (tau)
* rise time (0-100)
* halfwidth
* baseline value
* standard deviation of the baseline noise
* whether or not the mini is a compound mini

Each numerical column can be sorted by clicking on the column header.
The sort switches between highest-to-lowest and lowest-to-highest.

Export the data
--------------------

The selected data (``Ctrl+a`` to select all) can be copied and pasted to
Excel or text editors of choice. Data can be copied by ``Ctrl+c`` key stroke
or by ``right click`` on the data table -> ``Copy selected``.

The data can also be exported to a **comma separated value (CSV)** format
by ``file`` menu -> ``Mini Analysis`` -> ``Export datatable``. All data visible
in the data table are stored in the exported file.

Save the discovered minis
---------------------------

The data for the discovered minis can be stored in a format that can be
opened by SimplyFire later.

Go to ``file`` menu -> ``Mini Analysis`` -> ``Save minis as...`` and follow
the file save prompt.

The default extension for the mini data is ``.mini``.
The files can also be saved as ``.csv`` files and opened in other programs.
Mini data saved this way contains more details than data exported from
the data table.

Open previously analyzed minis
--------------------------------

Previously analyzed minis can be opened by
``file`` menu -> ``Mini Analysis`` -> ``Open mini file``.

Summarize the data
----------------------------------------

A summary of the discovered minis can be added to the  ``results display``.
The ``results display`` is found in the ``results`` tab under the plot.

``Right click`` on the data table -> ``Report all`` or ``Report selected``
to calculate the averages and standard deviations of the numerical properties
of the discovered minis.
The result can be found in the ``results display``. 
