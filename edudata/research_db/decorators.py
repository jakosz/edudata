
def html_row(content):
    def wrap(row):
        return "<tr>" + content(row) + "</tr>"
    return wrap

def html_bstrap_table(content):
    def wrap(data):
        return '<table border="1" class="table table-stripped table-bordered">' + content(data) + "</table>"
    return wrap

