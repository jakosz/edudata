# -*- coding:utf-8 -*-

import csv
import magic

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from django.core.files import File

# Error messages: TODO: unicode
err_msg = u'To nie jest poprawny plik csv; {0}.'
non_txt = u'podany plik powinien być typu tekstowego'
non_tab = u'we wszystkich wierszach liczba kolumn powinna być taka sama'
non_sep = u'separatorem kolumn powinien być średnik ( ; )'
non_quo = u'komórki zawierające tekst powinny być otoczone cudzysłowem ( " )'

# Checks if the file is of "text/plain" mimetype:
def is_txt(ff):
    if magic.from_buffer(File(ff).read(1024), mime = True) != 'text/plain':
        raise ValidationError, _(err_msg.format(non_txt))
    print 'is_txt: True'

# Checks if columns are separated with the desired character:
# (assumes at least two columns in the input file)
def is_sep_ok(ff, sep = ';', quote = '"'):
    f = csv.reader(ff, delimiter = sep, quotechar = quote)
    if len(f.next()) == 1:
        raise ValidationError, _(err_msg.format(non_sep))
    print 'is_sep_ok: True'

# Checks if all non-numeric cells are quoted with the desired character:
def is_quote_ok(ff, sep = ';', quote = '"'):
    f = File(ff)
    for row in f:
        cRow = row.split(sep)
        for cell in cRow:
            try:
                float(cell)
            except ValueError:
                if not cell.startswith(quote) and not cell.endswith(quote):
                    raise ValidationError, _(err_msg.format(non_quo))
    print 'is_quote_ok: True'

# Checks if number of columns is the same for all rows:
def is_table(ff, sep = ';', quote = '"'):
    f = csv.reader(ff, delimiter = sep, quotechar = quote)
    while True:
        try:
            if len(f.next()) != len(f.next()):
                raise ValidationError, _(err_msg.format(non_tab))
        except StopIteration:
            break
    print 'is_table: True'

# Performs all of the above tests; used as a validation function in edudata/models
def is_csv(FieldFile_file, sep = ';', quote = '"'):
    is_txt(FieldFile_file)
    is_table(FieldFile_file, sep = sep, quote = quote)
    is_sep_ok(FieldFile_file, sep = sep, quote = quote)
    is_quote_ok(FieldFile_file, sep = sep, quote = quote)
