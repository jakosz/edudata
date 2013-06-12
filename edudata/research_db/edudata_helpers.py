import csv

def is_csv(path, sep = ';', quote = '"'):
    ok = True
    with open(path, 'r') as f:
        c = csv.reader(f, delimiter = sep, quotechar = quote)
        while ok == True:
            try:
                if len(c.next()) == len(c.next()):
                    ok = True
                else:
                    ok = False
            except StopIteration:
                ok = True
                break
        return ok
