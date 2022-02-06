from .base_module import BaseModule
from tkinter import Toplevel
from SimplyFire import app
from .base_module_layout import BaseModuleLayout
class BaseModulePopup(Toplevel, BaseModuleLayout):
    def __init__(self,
                 module:BaseModule,
                 name:str=None
                 ) -> None:
        self.module = module
        self.visible=False
        super().__init__(app.root)
        super().withdraw()
        self.protocol('WM_DELETE_WINDOW', self._on_close)
        self.widgets = self.module.widgets
        self.name=name

    def show_window(self):
        self.visible = True
        self.deiconify()

    def withdraw_window(self):
        self.visible=False
        super().withdraw()
    def _on_close(self, event=None):
        self.visible = False
        super().withdraw()

    def enable(self):
        if self.visible:
            self.deiconify()
            self.lower(belowThis=app.root)
        else:
            pass

    def disable(self):
        super().withdraw()

    def hide(self):
        super().withdraw()
