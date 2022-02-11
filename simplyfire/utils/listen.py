import simplyfire
def to(event, function):
    simplyfire.app.root.bind(event, function, add='+')
