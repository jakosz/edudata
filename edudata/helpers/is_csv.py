# -*- coding:utf-8 -*-

import magic
import chardet
from warnings import warn

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from django.core.files import File

# ------------------------------------------------------------------------------ data

# [pl] Komunikaty błędu:
# [en] Error messages: 
err_msg = u'To nie jest poprawny plik csv; {0}.'
non_txt = u'podany plik powinien być typu tekstowego'
non_utf = u'podany plik powinien być zakodowany wg standardu utf-8'
non_tab = u'we wszystkich wierszach liczba kolumn powinna być taka sama'
non_sep = u'separatorem kolumn powinien być średnik ( ; )'
non_quo = u'komórki zawierające tekst powinny być otoczone cudzysłowem ( " ). Błąd został znaleziony w wierszu nr {0}'
hSpaces = u'nazwy zmiennych nie powinny zawierać znaku spacji'

# ------------------------------------------------------------------------------ functions

def gen2list(Generator):
    '''
    Converts generator object to list object
    '''
    List = []
    for item in Generator:
        List.append(item)
    return List

def list2gen(List):
    '''
    Converts list object to generator object
    '''
    for item in List:
        yield item

def dFile(ff, read = None):
    '''
    Opens django FieldFile and returns its contents (a list of strings, 
    typically). Its second argument (read) defines how many bytes should be 
    read; defaults to none.
    '''
    fo = File(ff)
    fo.open()
    return fo.read()

def paste_collapse(List):
    '''
    Recursively flattens list and pastes its elements into one string.
    Objects of a different type than str, int, float or list will be omitted
    and not included into output string. 
    '''
    paste = ''
    for i in List:
        if type(i) in [str, int, float]:
            paste = paste + str(i)
        elif type(i) is list:
            paste = paste + paste_collapse(i)
        else:
            pass
    return paste

def replace_newlines_in_cells(csvString, rep = ', ', quotechar = '"'):
    '''
    Replaces newline characters in non-numeric cells with string specified by 
    rep. Cells are defined as regions within given quotechars.
    '''
    csvList = list(csvString)
    switch = 0
    for i, char in enumerate(csvString):
        # decide whether char's inside a cell:
        if char == quotechar and switch == 0:
            switch = 1
        elif char == quotechar and switch == 1:
            switch = 0
        # if yes, replace newline:
        if char == '\n' and switch == 1:
            csvList[i] = rep
    return reduce(lambda x, y: x+y, csvList)

def csv2(ff, sep = ';', quote = '"'):
    '''
    Reads django FieldFile object (ff), converts it to a single string, 
    replaces newlines in cells with ', ' and returns a list of rows (each 
    containing a list of cells). Also, removes all Windows newline (\r) 
    characters. 
    '''
    csvString = replace_newlines_in_cells(paste_collapse(dFile(ff)), quotechar = quote)
    csvString = csvString.replace('\r', '')
    return [row.split(sep) for row in csvString.split('\n')[:-2]]

def is_txt(ff):
    '''
    Checks if a file is of text/* mimetype.
    '''
    if not magic.from_buffer(File(ff).read(1024), mime = True).startswith('text/'):
        raise ValidationError, _(err_msg.format(non_txt))
    print 'is_txt: True'

def is_utf8(ff):
    '''
    Checks (using chardet library) if a text file encoding is utf-8.
    '''
    ch = chardet.detect(dFile(ff))
    if not ch['encoding'] == 'utf-8' and not ch['encoding'] == 'ascii':
        if not ch['confidence'] == 0 and not ch['encoding'] == None:
            raise ValidationError, _(err_msg.format(non_utf))
        else:
            warn('is_utf8: chardet.detect couldn\'t determine file encoding')
    print 'is_utf8: True'


def is_quote_ok(csv2list, sep = ';', quote = '"', check_header = False):
    '''
    Checks if all non-numeric cells are quoted with the desired character.
    '''
    f = csv2list
    for i, cRow in enumerate(f[not check_header:]):
        print cRow
        for cell in cRow:
            try:
                # try to convert whatever you've found to a float:
                float(cell)
            except ValueError:
                # if it's impossible, then cell contents should be quoted:
                if not cell.startswith(quote) and not cell.endswith(quote) and not cell == '':
                    raise ValidationError, _(err_msg.format(non_quo.format(str(i + (not check_header)))))
    print 'is_quote_ok: True'

def is_table(csv2list, sep = ';', quote = '"'):
    '''
    Checks if a number of columns is the same in all rows.
    '''
    if len(set(map(len, csv2list))) != 1:
        raise ValidationError, _(err_msg.format(non_tab))
    print 'is_table: True'

def is_header_ok(csv2list, sep, quote):
    '''
    Checks if variable names in the header don't contain space characters.
    '''
    for col in csv2list[0]:
        if ' ' in col:
            raise ValidationError, _(err_msg.format(hSpaces))
    print 'is_header_ok: True'

def is_sep_ok(csv2list, sep = ';', quote = '"'):
    '''
    Checks if columns are separated with the desired character. 
    Assumes that the input file consists of at least two columns.
    '''
    col_len_list = set(map(len, csv2list))
    for col in col_len_list:
        if col < 2:
            raise ValidationError, _(err_msg.format(non_sep))
    print 'is_sep_ok: True'

def is_csv(FieldFile_file, sep = ';', quote = '"'):
    '''
    Performs all of the is_* tests.
    Used as a validation function in edudata/models.
    '''
    # Buffer checks:
    is_txt(FieldFile_file)
    is_utf8(FieldFile_file)
    # File structure checks:
    parsed_csv = csv2(FieldFile_file)
    is_header_ok(parsed_csv, sep = sep, quote = quote)
    is_sep_ok(parsed_csv, sep = sep, quote = quote)
    is_table(parsed_csv, sep = sep, quote = quote)
    is_quote_ok(parsed_csv, sep = sep, quote = quote)
