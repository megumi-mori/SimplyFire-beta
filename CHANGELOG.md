# Changelog

## Beta 0.3.3

- print load log with load time ([#24](https://github.com/megumi-mori/SimplyFire-beta/issues/24))

## Beta 0.3.2

- fix build error

## Beta 0.3.1

- Compare plugin bug fix - stores default style values for 'undo' values
- Baseline std for compound mini is the baseline std of the base mini
- handle drawrect error in ``trace_display`` - rect object can be deleted by
  other parts of the code
- mini_GUI does not delete ``.mini`` files during undo
- checks in place to only delete temp files located within the temp directory
- compare plugin does not change the viewing axes limits when adding or
  removing recording files
  (unless the maximum axes limits are changed)
- The plugin manager defaults to the package folder when no plugins can be found
  in the user-specified data folder.

## Beta 0.3.0

- SimplyFire-beta made public
- Plugins can be activated/inactivated
- Bug fixes for mini finding algorithm (compound minis)

## Past releases

- warning message when config directory cannot be found ([#19](https://github.com/megumi-mori/PyMini/issues/19))
- option to save all settings while the session is in progress.
