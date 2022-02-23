Evoked Amplitude Analysis
==========================

Overview
---------
Goal:
  Calculate the amplitude of evoked release (EPSP, EPSC, EJC, EJP)
  and determine the 'average' amplitude for a recording

Output:
  * Processed recording data with adjusted baseline
  * Exportable table of maximum and minimum amplitudes
  * Summary of the data

Plugins used:
  * :doc:`../plugin_gui/navigation` (optional)
  * :doc:`../plugin_gui/sweeps` (optional)
  * :doc:`../plugin_gui/process`
  * :doc:`../plugin_gui/evoked_basic`


Set up
-------

:ref:`open-recording` from ``file`` menu -> ``Open recording`` or ``Alt+o``.
Set the view mode to ``overlay`` by ``View`` menu -> ``overlay``
Select the channel to analyze in the channel dropdown menu.

Open plugins to use by ``Plug-ins`` menu -> select the desired plugin names.
Plugins typically have user-input forms that appear in the **control-panel**
as individual tabs.

Use the :doc:`../plugin_gui/process` to subtract the baseline.
Find a x-axis region that best estimates the 'baseline' in the recording.
Set the Baseline Subtraction method to ``Mean of x-axis range`` and
enter the lower and upper bounds of the x-axis used to calculate the baseline
for each sweep.
Click ``Apply``.
The baseline of the sweeps should now be aligned at y=0.

Save the recording file by ``file`` menu -> ``Save recording data as...``.

.. Caution::
  ``.abf`` files cannot be overwritten by SimplyFire.
  Baseline subtracted traces should be stored under a new file name.

If the amplitude of the artefact is larger than the evoked response,
use the :ref:`navigation-tools` located around the plot to adjust
the x- and y-axes so that the artefact is outside of the visible x-axis.

Alternatively, use the :doc:`../plugin_gui/navigation` to set the desired x- and y-axes
limits.

If not all sweeps should be analyzed (i.e. some sweeps failed to respond),
use the :doc:`../plugin_gui/sweeps` to hide unwanted sweeps.
While the :doc:`../plugin_gui/sweeps` is in focus, a sweep can be highlighted
by clicking on or near the sweep.
Pressing the ``Delete``/``Backspace``/``e`` key will hide the sweep from view.

The sweeps that are currently visible are indicated in the **control-panel**.

Analysis
----------

Analysis is performed by the :doc:`../plugin_gui/evoked_basic`.

If the artefact is larger than the evoked response, set the
``Limit x-axis for analysis to:  `` parameter to ``Visible window`` and adjust
the plot so that the artefact are outside of the visible window.

Alternatively, set the ``Limit x-axis for analysis to:  `` parameter to
``Defined range  `` and enter the lower and upper x-axis limits for the analysis.

Click on ``Calculate Min/Max  `` button.
Minimum and maximum values per sweep (per channel, if multiple channels are analyzed)
will be entered into the data panel.


Output
-----------

The results of the analysis can be found in the data panel.

The following properties for each sweep analyzed can be found:
  * Sweep number (starting from 0)
  * Channel number
  * Filename
  * Minimum y-value for the sweep
  * Maximum y-value for the sweep

Export the data
^^^^^^^^^^^^^^^^

Selected entries in the **data panel** can be copied onto the
clipboard.

Press ``Shift`` and ``left-click`` to select a range of entries
or press ``Ctrl`` and select multiple entries.
Use ``Ctrl+a`` to select all entries.
Use the ``Escape``/``q`` key to remove all the highlights.

Data can be copied by ``Ctrl+c`` key stroke
or ``right-click`` on the **data-panel** -> ``Copy selected``.

The copied data can be pasted into Excel or other programs of choice.

The **data-panel** can also be exported to a **comma separated value (CSV)** format
by ``file`` menu -> ``Mini Analysis`` -> ``Export data table``. All data visible
in the **data-panel** are stored in the exported file.

Summarize the data
^^^^^^^^^^^^^^^^^^^^^^

A summary of the discovered minis can be added to the  **results-display**.
The **results-display** is found in the ``results`` tab under the plot.

``Right-click`` on the **data-panel** -> ``Report all`` or ``Report selected``
or press the ``Report stats`` on the **control-panel**. Averages and standard
deviation of maximum/minimum y-values will be added to the **results-display**.
Additionally, the indices of channels and sweeps sampled will be indicated.

The result can be found in the **results-display**.


Clear the data
-----------------
When opening a new recording file, the data in the **data-panel** are cleared.

The entries can also be deleted by selecting the entries and using
``Delete``/``Backspace``/``e`` key.

Alternatively, the ``Delete all`` button in the **control-panel** can be pressed.
