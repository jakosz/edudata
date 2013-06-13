import csv
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

def is_csv(FieldFile_file, sep = ';', quote = '"'):
    ok = True
    c = csv.reader(FieldFile_file, delimiter = sep, quotechar = quote)
    while ok == True:
        try:
            if len(c.next()) == len(c.next()):
                ok = True
            else:
                raise ValidationError, _("To nie jest plik typu CSV (separator to srednik, tekst ograniczony \"tekst\"")
        except StopIteration:
            ok = True
            break
    return ok
