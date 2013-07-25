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

# [pl] ------------------------------------------------------------------------- Funkcje pomocnicze:

def t2f(x):
    '''text to float'''
    try:
        if ',' in x:
            x = x.replace(',', '.')
    except TypeError:
        pass
    return float(x)

# TODO:
# def Pobierz wartości z kolumny "etykieta", żeby uwzględnić je w testach min/max

# [pl] ------------------------------------------------------------------------- Komunikaty błędów ze skryptu Mateusza:
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

# [pl] ------------------------------------------------------------------------- Funkcje sprawdzające:

def names(cb, df):
    ''' [pl] NAZWA; kol. 1 '''
    # [pl] Czy nazwy kolumn w df są unikalne?
    if len(set(df.columns)) != len(df.columns):
        raise CodebookDataframeIntegrityError(_(u'Nazwy kolumn w zbiorze danych nie są unikalne.'))
    # [pl] Czy nazwy kolumn df w cb są unikalne?
    if len(set(cb.iloc[:, 0])) != len(cb.iloc[:, 0]):
        raise CodebookDataframeIntegrityError(_(u'Nazwy kolumn wyszczególnione w codebooku nie są unikalne.'))
    # [pl] Czy zbiory stringów w nagłówku df i pierwszej kolumnie cb są takie same?
    if False in [NAZWA in df.columns for NAZWA in cb.iloc[:, 0]]:
        raise CodebookDataframeIntegrityError(_(u'Nazwy kolumn w zbiorze danych są inne niż te podane w codebooku.'))
    print 'codebook/dataframe names checked.'

def descriptions(cb):
    '''
    [pl] Czy wszystkie komórki są wypełnione?
    [pl] OPIS, OPIS2, SLOWA; kol. 2:4; 
    '''
    for iCol in [1,2,3]:
        tests = [(cb.iloc[:, iCol] == '').value_counts(), 
                 p.isnull(cb.iloc[:, iCol]).value_counts()]
        for t in tests:
            if len(t) == 2 or (len(t) == 1 and t.index[0] == True):
                warn(_('Nie wszystkie komórki w kolumnie {0} zostały wypełnione'.format(str(cb.columns[iCol]))))
    print 'codebook/dataframe descriptions checked.'

def sizeval_size(cb, df):
    '''
    [pl] Czy rozmiary zmiennych odpowiadają deklaracjom z codebooka?
    [pl] ROZMIAR; kol. 7;
    '''
    # [pl] Komunikat błędu:
    eText = u'Rozmiar zmiennej w kolumnie {0} jest inny niż zadeklarowano w codebooku'
    # [pl] Dla każdej kolumny w ramce danych...
    for iCol, vals in enumerate(df.columns):
        # [pl] ...wyznacz maksymalny rozmiar zmiennej (długość po konwersji do stringa)...
        max_size = sorted(set([len(unicode(i)) for i in df.iloc[:, iCol]]))[-1]
        # [pl] ...i sprawdź, czy nie jest większy niż deklaracja w codebooku:
        if max_size > cb.iloc[iCol, 6]:
            raise CodebookDataframeIntegrityError(_(eText.format(str(iCol+1))))
    print 'codebook/dataframe variable size checked.'

def sizeval_precision(cb, df, v=0):
    '''
    [pl] Czy dokładności zmiennych odpowiadają deklaracjom z codebooka?'
    [pl] DOKLADNOSC; kol. 8;
    '''
    # [pl] Komunikat błędu:
    eText = u'Dokładność zmiennej w kolumnie {0} jest inna niż zadeklarowano w codebooku'
    # [pl] Pomocnicza: split wg zadanego znaku + sprawdzenie zgodności db/cb:
    def chkDec(dec, iCol):
        # [pl] Wyznacz maksymalną dokładność zmiennej w kolumnie iCol dla znaku dziesiętnego dec...
        max_precision = sorted(set([len(i.split(dec)[1]) for i in df.iloc[:,iCol]]))[-1]
        # [pl] ...i sprawdź, czy nie jest większa niż deklaracja w codebooku:
        if max_precision > cb.iloc[iCol, 7]:
            raise CodebookDataframeIntegrityError(_(eText.format(str(iCol+1))))
    # [pl] Zastosuj chkDec dla obu wariantów znaku dziesiętnego...
    for iCol, vals in enumerate(df.columns):
        try:
            # [pl] ...tylko do tych kolumn, w których wszystkie komórki zawierają
            # [pl] dany znak dziesiętny i dla których w codebooku podano jakąkolwiek dokładność:
            if all([',' in i for i in df.iloc[:,iCol]]) and not p.isnull(cb.iloc[iCol, 7]):
                chkDec(',', iCol)
            elif all(['.' in i for i in df.iloc[:,iCol]]) and not p.isnull(cb.iloc[iCol, 7]):
                chkDec('.', iCol)
            else:
                pass
            # [en] Verbosity:
            if v > 0:
                print 'sizeval_precision: checked col {0}'.format(str(iCol))
        except TypeError:
            # [en] Verbosity:
            if v > 0:
                print 'sizeval_precision: skipping non-float argument.'
    print 'codebook/dataframe variable precision checked.'

def sizeval_minmax(cb, df):
    '''
    [pl] Czy dokładności zmiennych odpowiadają deklaracjom z codebooka?'
    [pl] WART_MIN, WART_MAX; kol. 9:10;
    '''
    # [pl] Komunikat błędu:
    eText = u'Wartość zmiennej {0} (kolumna {1}) jest {2} niż wartość {3} zadeklarowana dla tej zmiennej w codebooku'
    for iCol, vals in enumerate(df.columns):
        if any([t2f(i) < cb.iloc[iCol, 8] for i in df.iloc[:, iCol]]):
            raise CodebookDataframeIntegrityError(eText.format(df.columns[iCol], str(iCol+1), u'mniejsza', u'minimalna'))
        if any([t2f(i) > cb.iloc[iCol, 9] for i in df.iloc[:, iCol]]):
            raise CodebookDataframeIntegrityError(eText.format(df.columns[iCol], str(iCol+1), u'większa', u'maksymalna'))
    print 'codebook/dataframe variable range checked.'

def sizeval_values(df):
    ''' [pl] Czy wszystkie zmienne w zbiorze mają (w ogóle, jakiekolwiek) wartości? '''
    for i, v in enumerate(df.columns):
        if any(p.isnull(df.iloc[:,i])):
            raise CodebookDataframeIntegrityError(u'Brak wartości w zmiennej {0} (kolumna {1})'.format(df.columns[i], str(i+1)))

# sizeval_values(df)

def sizeval(cb, df):
    # ROZMIAR
    sizeval_size(cb, df)
    # DOKLADNOSC
    sizeval_precision(cb, df)
    # WART_MIN, WART_MAX
    sizeval_minmax(cb, df)
    # 4=>"Zmienna nie ma wartości",
    sizeval_values(df)
    # 5=>"Zmienna ma wartość niezgodną z typem zmiennej %1 != %2",
    sizeval_types(cb, df)
    sizeval_labels(cb, df)

# sizeval(cb, df)

# [pl] ------------------------------------------------------------------------- Funkcje TODO:

def conditions(cb, df):
    # WARUNEK
    pass

def types(cb, df):
    # TYP
        # Czy nazwy typów pasują do słownika nazw?
    pass

def scales(cb, df):
    # SKALA
        # Czy nazwy skal pasują do słownika nazw?
    pass

def labels(cb):
    ''' [pl] Czy wszystkim zmiennym przypisano etykiety? '''
    pass

def sizeval_labels(cb, df):
    ''' [pl] Czy zmienna ma wartość spoza zakresu etykiet opisanych w codebook-u? '''
    pass
