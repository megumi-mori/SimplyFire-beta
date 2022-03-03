# Changelog

## Beta 0.3.1

- Compare plugin bug fix - stores default style values for 'undo' values
- Baseline std for compound mini is the baseline std of the base mini
- handle drawrect error in ``trace_display`` - rect object can be deleted by other
  parts of the code
- mini_GUI does not delete ``.mini`` files during undo
- checks in place to only delete temp files located within the temp directory

## Beta 0.3.0

- SimplyFire-beta made public
- Plugins can be activated/inactivated
- Bug fixes for mini finding algorithm (compound minis)

## Past releases

- warning message when config directory cannot be found ([#19](https://github.com/megumi-mori/PyMini/issues/19))
- option to save all settings while the session is in progress.
