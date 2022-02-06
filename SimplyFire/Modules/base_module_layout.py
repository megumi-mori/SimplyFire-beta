from SimplyFire import app

class BaseModuleLayout():
    """
    parent class for module GUI components
    the child class must implement the following fucntions that returns a bool for the event binding to work:

    is_enabled
    has_focus
    is_visible


    """
    def __init__(self, module):
        self.module=module
        pass

    def call_if_enabled(self, function):
        if self.is_enabled():
            function()

    def call_if_focus(self, function):
        if self.has_focus():
            function()

    def call_if_visible(self, function):
        if self.is_visible():
            function()

    def listen_to_event(self, event:str, function, condition:str=None, target=app.root):
        assert condition in {'focused', 'enabled', 'visible', None}, 'condition must be None, "focus", or "enabled"'
        # assert callable(function), f'{function} is not callable'
        if condition is None:
            target.bind(event, lambda e:function(), add="+")
        elif condition == 'enabled':
            target.bind(event, lambda e, f=function:self.call_if_enabled(f), add='+')
        elif condition == 'focused':
            target.bind(event, lambda e, f=function:self.call_if_focus(f), add="+")
        elif condition == 'visible':
            target.bind(event, lambda e, f=function: self.call_if_visible(f), add='+')

