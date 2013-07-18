# -*- encoding: utf-8 -*-

import numpy as n
import pandas as p
from warnings import warn

'''
    [pl] Te testy przeprowadzane są dopiero *po* sprawdzeniu ich przez is_csv (przy wgrywaniu).
    [en] These tests are run *after* is_csv tests are performed (on upload).
         Standard IBE codebook has the form ...
'''

'''[en]
All of the following tests require converting both codebook and dataframe 
to pandas DataFrame class.
'''

df = p.read_csv('/media/truecrypt13/mhnatiuk/edudata/test/df.csv', sep = ';', quotechar = '"', encoding='utf-8')
cb = p.read_csv('/media/truecrypt13/mhnatiuk/edudata/test/codebook.csv', sep = ';', quotechar = '"', encoding='utf-8')

# [en] Error class for tests in this module:
class CodebookDataframeIntegrityError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class cbdfit:
    def __init__(self):
        # Docelowo to chyba powinny być indeksy kolumn, a nie nazwy; p. Issue #33.
        self.cb_names = ['NAZWA', 'OPIS', 'OPIS2', 'SLOWA', 'TYP', 'SKALA', 
                         'ROZMIAR', 'DOKLADNOSC', 'WART_MIN', 'WART_MAX', 
                         'ETYKIETA', 'WARUNEK']

# Komunikaty błędów ze skryptu Mateusza:
    # 0=>"Wiersz nie zawiera zmiennej ",
    # 1=>"Zmienna ma wartość, choć powinna być pusta (jest to zmienna typy u 'kategoria')",
    # 2=>"Zmienna nie ma wartości choć z filtru wynika, że powinna",
    # 3=>"Zmienna ma wartość choć z filtru wynika, że nie powinna",
    # 4=>"Zmienna nie ma wartości",
    # 5=>"Zmienna ma wartość niezgodną z typem zmiennej %1 != %2",
    # 6=>"Zmienna ma wartość dłuższą, niż rozmiar określony w codebook-u",
    # 7=>"Zmienna ma dokładność większą, niż określona w codebook-u",
    # 8=>"Zmienna ma wartość spoza zakresu opisanego w codebook-u",
    # 9=>"Zmienna ma wartość spoza zakresu etykiet opisanych w codebook-u (%1)",
    # 10=>"Wiersz zawiera zmienne niezdefiniowane w codebook-u"

# [pl] NAZWA; kol. 1
def names(cb, df):
    # [pl] Czy nazwy kolumn w df są unikalne?
    if len(set(df.columns)) != len(df.columns):
        raise CodebookDataframeIntegrityError(_(u'Nazwy kolumn w zbiorze danych nie są unikalne.'))
    # [pl] Czy nazwy kolumn df w cb są unikalne?
    if len(set(cb.iloc[:, 0])) != len(cb.iloc[:, 0]):
        raise CodebookDataframeIntegrityError(_(u'Nazwy kolumn wyszczególnione w codebooku nie są unikalne.'))
    # [pl] Czy zbiory stringów w nagłówku df i pierwszej kolumnie cb są takie same?
    if False in [NAZWA in df.columns for NAZWA in cb.iloc[:, 0]]:
        raise CodebookDataframeIntegrityError(_(u'Nazwy kolumn w zbiorze danych są inne niż te podane w codebooku.'))
    # XXX: ETYKIETA
    print 'codebook/dataframe names checked.'

# [pl] OPIS, OPIS2, SLOWA; kol. 2:4
def descriptions(cb):
    # [pl] Czy wszystkie komórki są wypełnione?
    for iCol in [1,2,3]:
        tests = [(cb.iloc[:, iCol] == '').value_counts(), 
                 p.isnull(cb.iloc[:, iCol]).value_counts()]
        for t in tests:
            if len(t) == 2 or (len(t) == 1 and t.index[0] == True):
                warn(_('Nie wszystkie komórki w kolumnie '+str(cb.columns[iCol])+' zostały wypełnione'))
    print 'codebook/dataframe descriptions checked.'

def types(cb, df):
    # TYP
        # Czy nazwy typów pasują do słownika nazw?
    pass

def scales(cb, df):
    # SKALA
        # Czy nazwy skal pasują do słownika nazw?
    pass

def sizeval(cb, df):
    # ROZMIAR
        # Czy rozmiary Danych są mniejsze lub równe rozmiarom Codebooka?
    # DOKLADNOSC
    # WART_MIN
    # WART_MAX
    pass

def conditions(cb, df):
    # WARUNEK
    pass
