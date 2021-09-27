from utils.widget import DataTable


trace_header = [
    'sweep',
    'state'
]

def load(parent=None):
    global datatable
    datatable = DataTable(parent)

    global table
    table = datatable.table

    datatable.define_columns(tuple(trace_header))

    return datatable