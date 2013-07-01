# -*- coding:utf-8 -*-

import csv
import magic
import chardet
from warnings import warn

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from django.core.files import File

# [pl] Komunikaty błędu:
# [en] Error messages: 
err_msg = u'To nie jest poprawny plik csv; {0}.'
non_txt = u'podany plik powinien być typu tekstowego'
non_utf = u'podany plik powinien być zakodowany wg standardu utf-8'
non_tab = u'we wszystkich wierszach liczba kolumn powinna być taka sama, tymczasem liczba kolumn w wierszu nr 1 i wierszu nr {0} jest różna.'
non_sep = u'separatorem kolumn powinien być średnik ( ; ). Błąd został znaleziony w wierszu nr {0}.'
non_quo = u'komórki zawierające tekst powinny być otoczone cudzysłowem ( " ). Błąd został znaleziony w wierszu nr {0}.'
hSpaces = u'nazwy zmiennych nie powinny zawierać znaku spacji.'

# Checks if a file is of "text/.*$" mimetype:
def is_txt(ff):
    if not magic.from_buffer(File(ff).read(1024), mime = True).startswith('text/'):
        raise ValidationError, _(err_msg.format(non_txt))
    print 'is_txt: True'

# Checks if a text file encoding is utf-8:
def is_utf8(ff):
    if not chardet.detect(File(ff).read(1024))['encoding'] == 'utf-8':
        if not chardet.detect(File(ff).read(1024))['confidence'] == 0 or not chardet.detect(File(ff).read(1024))['encoding'] == None:
            raise ValidationError, _(err_msg.format(non_utf))
        else:
            warn('is_utf8: chardet.detect couldn\'t determine file encoding')
    print 'is_utf8: True'

# Checks if all non-numeric cells are quoted with the desired character:
def is_quote_ok(ff, sep = ';', quote = '"', check_header = False):
    f = File(ff).read()
    for i, row in enumerate(f[check_header:]):
        cRow = row.split(sep)
        for cell in cRow:
            try:
                float(cell)
            except ValueError:
                if not cell.startswith(quote) and not cell.endswith(quote):
                    raise ValidationError, _(err_msg.format(non_quo.format(str(i))))
    print 'is_quote_ok: True'

# Checks if a number of columns is the same for all rows:
def is_table(ff, sep = ';', quote = '"'):
    f = csv.reader(ff, delimiter = sep, quotechar = quote)
    rowCounter = 0
    firstRow = f.next()
    while True:
        try:
            rowCounter += 1
            if len(firstRow) != len(f.next()):
                raise ValidationError, _(err_msg.format(non_tab.format(str(rowCounter+1))))
        except StopIteration:
            break
    print 'is_table: True'

# Checks if variable names in the header don't contain space characters:
def is_header_ok(ff, sep, quote):
    f = csv.reader(ff, delimiter = sep, quotechar = quote)
    header = f.next()
    for col in header:
        if ' ' in col:
            raise ValidationError, _(err_msg.format(hSpaces))
    print 'is_header_ok: True'

# Checks if columns are separated with the desired character:
# Assumes at least two columns in the input file. 
# Assumes that is_table test was done. 
# TODO: find a better way of verifying sep correctness
def is_sep_ok(ff, sep = ';', quote = '"'):
    f = csv.reader(ff, delimiter = sep, quotechar = quote)
    if len(f.next()) == 1:
        raise ValidationError, _(err_msg.format(non_sep))
    print 'is_sep_ok: True'

# Performs all of the above tests; used as a validation function in edudata/models
def is_csv(FieldFile_file, sep = ';', quote = '"'):
    is_txt(FieldFile_file)
    is_utf8(FieldFile_file)
    is_sep_ok(FieldFile_file, sep = sep, quote = quote)
    is_quote_ok(FieldFile_file, sep = sep, quote = quote)
    is_header_ok(FieldFile_file, sep = sep, quote = quote)
    is_table(FieldFile_file, sep = sep, quote = quote)
