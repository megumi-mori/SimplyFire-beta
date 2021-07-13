from utils.widget import DataTable

def load(parent=None):
    global frame
    frame = DataTable(parent)

    global table
    table = frame.table

    return frame