# -*- encoding: utf-8 -*-

import re
import numpy as n
import pandas as p
from warnings import warn
from multiprocessing import Pool

'''
    [pl] Te testy przeprowadzane są dopiero *po* sprawdzeniu ich przez is_csv (przy wgrywaniu).
    [en] These tests are run *after* is_csv tests are performed (on upload).
    [en] Standard IBE codebook has the form ...
'''

'''
    [en] All of the following tests require converting both codebook and dataframe 
    [en] to pandas DataFrame class.
'''

# [pl] ------------------------------------------------------------------------- Funkcje pomocnicze:

class CodebookDataframeIntegrityError(Exception):
    ''' [en] Error class for tests in this module [/en] '''
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class CbdfitMethodError(CodebookDataframeIntegrityError):
    ''' [en] Error class for methods in class cbdfit [/en] '''
    pass

def t2f(x):
    '''text to float'''
    """
    TODO: [pl] Zmienie to na funkcje C dla poprawy wydajnosci [/pl]
    """
    
    try:
        if ',' in x:
            x = x.replace(',', '.')
    except TypeError:
        pass
    return float(x)

def collapse(List, sep = ', '):
    return reduce(lambda x,y: str(x)+sep+str(y), List)

def re_any(reList, inList):
    ''' [pl] 
    Czy listy reList i inList mają *jakikolwiek* wspólny element (w tym substring)?
    1) Lista reList może zawierać wyrażenia regularne...
    2) ...więc test jest wrażliwy na znaki początku/końca stringa (^/$)!
    '''
    for Re in reList:
        for In in inList:
            if len(re.findall(Re, In)) != 0:
                return True
    return False

def any_re(reList, inString):
    ''' [pl] 
    Czy *którykolwiek* element reList znajduje się w stringu inString?
    1) Lista reList może zawierać wyrażenia regularne...
    2) ...więc test jest wrażliwy na znaki początku/końca stringa (^/$)!
    '''
    for Re in reList:
        if len(re.findall(Re, inString)) != 0:
            return True
    return False

def prepare_operator(string):
    ''' [pl] Przekształca operatory z kolumny WARUNEK do postaci parsowalnej przez Pythona [/pl] '''
    if string == '=':
        string = '=='
    return string

def conditions_get(cb, df):
    ''' [pl] Zwraca słownik, w którym kluczami są nazwy zmiennych warunkowych, 
    a wartościami listy wartości logicznych zdających sprawę z tego, czy dla
    danego wiersza (odpowiadającego elementowi listy) warunek został spełniony [/pl] '''
    test = {}
    for i, v in enumerate(df.columns):
        if not p.isnull(cb.iloc[i,-1]):
            cond = cb.iloc[i,-1].split(' ')
            operator = prepare_operator(cond[1])
            value = cond[2]
            test[v] = [eval(str(cell)+operator+value) for cell in df[cond[0]]]
    return test

def labels_get(cb_CELL):
    ''' [pl] 
    Pobierz wartości z *komórki* i zwróć je jako słownik 
    Zakłada istnienie składni opisu etykiet w kolumnie ETYKIETA
    [/pl] '''
    res = {}
    try:
        List = [c.split(':') for c in cb_CELL.split('\n')]
        for item in List:
            res[item[0]] = item[1]
    except AttributeError:
        pass
    return res

# [pl] ------------------------------------------------------------------------- Klasa testująca:

class cbdfit:
    def __init__(self, msg_mode = 'report', verbosity = None):
        self.cb_types = ['liczba ca.+kowita', 'liczba rzeczywista', 'tekst']
        self.cb_scales = ['porz.+dkowa', 'nominalna', 'ilorazowa', 'dychotomiczna']
        ''' [pl] cb_names zostało dodane na potrzeby ewentualnych rozszerzeń;
        obecnie funkcje w tym module korzystają z indeksów a nie z nazw kolumn: [/pl] '''
        self.cb_names = ['NAZWA', 'OPIS', 'OPIS2', 'SLOWA', 'TYP', 'SKALA', 
                         'ROZMIAR', 'DOKLADNOSC', 'WART_MIN', 'WART_MAX', 
                         'ETYKIETA', 'WARUNEK']
        self.msg_mode = msg_mode
        self.v = verbosity
        self.report = []

    def msg(self, msg, mode, v = None):
        '''
        [pl] Ta funkcja pozwala na ustalenie typu komunikatu błędu [/pl]
        '''
        if mode not in ['error', 'warn', 'report']:
            raise CbdfitMethodError(_('msg: "error", "warn" i "report" to jedyne dopuszczalne wartości argumentu mode'))
        if mode == 'error':
            raise CodebookDataframeIntegrityError(_(msg))
        if mode == 'warn':
            warn(_(msg))
        if mode == 'report':
            self.report.append(msg)
            print msg

    def values(self, df, v = None):
        ''' [pl] Czy wszystkie zmienne w zbiorze mają (w ogóle, jakiekolwiek) wartości? [/pl] '''
        for i, val in enumerate(df.columns):
            if any(p.isnull(df.iloc[:,i])):
                self.msg(u'Brak wartości w zmiennej {0} (kolumna {1})'.format(df.columns[i], str(i+1)), self.msg_mode)
        print 'codebook/dataframe names checked.'

    def names(self, cb, df, v = None):
        ''' [pl] NAZWA; kol. 1 [/pl] '''
        # [pl] Czy nazwy kolumn w df są unikalne?
        if len(set(df.columns)) != len(df.columns):
            self.msg(u'Nazwy kolumn w zbiorze danych nie są unikalne.', self.msg_mode)
        # [pl] Czy nazwy kolumn df w cb są unikalne?
        if len(set(cb.iloc[:, 0])) != len(cb.iloc[:, 0]):
            self.msg(u'Nazwy kolumn wyszczególnione w codebooku nie są unikalne.', self.msg_mode)
        # [pl] Czy zbiory stringów w nagłówku df i pierwszej kolumnie cb są takie same?
        if False in [NAZWA in df.columns for NAZWA in cb.iloc[:, 0]]:
            self.msg(u'Nazwy kolumn w zbiorze danych są inne niż te podane w codebooku.', self.msg_mode)
        print 'codebook/dataframe names checked.'

    def descriptions(self, cb, v = None):
        ''' [pl]
        Czy wszystkie komórki są wypełnione?
        OPIS, OPIS2, SLOWA; kol. 2:4; 
        [/pl] '''
        for iCol in [1,2,3]:
            t = p.isnull(cb.iloc[:, iCol]).value_counts()
            if len(t) == 2 or (len(t) == 1 and t.index[0] == True):
                self.msg('Nie wszystkie komórki w kolumnie {0} zostały wypełnione'.format(str(cb.columns[iCol])), self.msg_mode)
        print 'codebook/dataframe descriptions checked.'

    def types(self, cb, df, v = None):
        ''' [pl] TYP; kol. 5 [/pl] '''
        # [pl] Czy wszędzie podano typy?
        if any(p.isnull(cb.iloc[:,4])):
            self.msg(u'Nie dla wszystkich zmiennych określono typ', self.msg_mode) # TODO dla których?
        # [pl] Czy nazwy typów pasują do słownika nazw?
        for cb_value in set(cb.iloc[:,4]):
            if not any_re(self.cb_types, unicode(cb_value).lower()):
                self.msg(u'Nieznany typ zmiennej: {}'.format(unicode(cb_value)), self.msg_mode) # TODO numer wiersza
        # [pl] Czy zmienne mają wartości zgodne z zadeklarowanymi typami?
        for i, name in enumerate(df.columns):
            if len(re.findall('liczba ca.+kowita', cb.iloc[i, 4].lower())) != 0:
                pass # TODO
            if len(re.findall('liczba rzeczywista', cb.iloc[i, 4].lower())) != 0:
                pass # TODO
            if len(re.findall('tekst', cb.iloc[i, 4].lower())) != 0:
                pass # TODO
        print 'codebook/dataframe types checked.'

    def scales(self, cb, df, v = None):
        ''' [pl] SKALA; kol. 6 [/pl] '''
        # [pl] Czy wszędzie podano skale?
        if any(p.isnull(cb.iloc[:,5])):
            self.msg(u'Nie dla wszystkich zmiennych określono typ', self.msg_mode)
        # [pl] Czy nazwy skal pasują do słownika nazw?
        for cb_value in set(cb.iloc[:,5]):
            if not any_re(self.cb_scales, unicode(cb_value).lower()):
                self.msg(u'Nieprawidłowa skala zmiennej: {}'.format(unicode(cb_value)), self.msg_mode)
        print 'codebook/dataframe scales checked.'

    def size(self, cb, df, v = None):
        ''' [pl]
        Czy rozmiary zmiennych odpowiadają deklaracjom z codebooka?
        ROZMIAR; kol. 7;
        [/pl] '''
        # [pl] Komunikat błędu:
        eText = u'Rozmiar zmiennej w kolumnie {0} jest inny niż zadeklarowano w codebooku'
        # [pl] Dla każdej kolumny w ramce danych...
        for iCol, vals in enumerate(df.columns):
            # [pl] ...wyznacz maksymalny rozmiar zmiennej (długość po konwersji do stringa)...
            max_size = sorted(set([len(unicode(i)) for i in df.iloc[:, iCol]]))[-1]
            # [pl] ...i sprawdź, czy nie jest większy niż deklaracja w codebooku:
            if max_size > cb.iloc[iCol, 6]:
                self.msg(eText.format(str(iCol+1)), self.msg_mode)
        print 'codebook/dataframe variable size checked.'

    def precision(self, cb, df, v = None):
        ''' [pl]
        Czy dokładności zmiennych odpowiadają deklaracjom z codebooka?'
        DOKLADNOSC; kol. 8;
        [/pl] '''
        # [en] Default class-wide verbosity argument [/en]:
        if v is None:
            v = self.v
        # [pl] Komunikat błędu: [/pl]
        eText = u'Dokładność zmiennej w kolumnie {0} jest inna niż zadeklarowano w codebooku'
        # [pl] Pomocnicza: split wg zadanego znaku + sprawdzenie zgodności db/cb: [/pl]
        def chkDec(dec, iCol):
            # [pl] Wyznacz maksymalną dokładność zmiennej w kolumnie iCol dla znaku dziesiętnego dec... [/pl]
            max_precision = sorted(set([len(i.split(dec)[1]) for i in df.iloc[:,iCol]]))[-1]
            # [pl] ...i sprawdź, czy nie jest większa niż deklaracja w codebooku: [/pl]
            if max_precision > cb.iloc[iCol, 7]:
                self.msg(eText.format(str(iCol+1)), self.msg_mode)
        # [pl] Zastosuj chkDec dla obu wariantów znaku dziesiętnego... [/pl]
        for iCol, vals in enumerate(df.columns):
            try:
                ''' [pl] ...tylko do tych kolumn, w których wszystkie komórki zawierają
                dany znak dziesiętny i dla których w codebooku podano jakąkolwiek dokładność: [/pl] '''
                if all([',' in i for i in df.iloc[:,iCol]]) and not p.isnull(cb.iloc[iCol, 7]):
                    chkDec(',', iCol)
                elif all(['.' in i for i in df.iloc[:,iCol]]) and not p.isnull(cb.iloc[iCol, 7]):
                    chkDec('.', iCol)
                else:
                    pass
                # [en] Verbosity: [/en]
                if v > 0:
                    print 'sizeval_precision: checked col {0}'.format(str(iCol))
            except TypeError:
                # [en] Verbosity: [/en]
                if v > 0:
                    print 'sizeval_precision: skipping non-float argument.'
        print 'codebook/dataframe variable precision checked.'

    def minmax(self, cb, df, v = None):
        # TODO: wartości braków danych z kolumny ETYKIETA.
        # FIXME: strasznie wolne (przy pandas.apply też), przepisać
        ''' [pl]
        Czy dokładności zmiennych odpowiadają deklaracjom z codebooka?'
        WART_MIN, WART_MAX; kol. 9:10;
        [/pl] '''
        if v is None:
            v = self.v
        # [pl] Komunikat błędu [/pl]
        eText = u'Zmienna {0} (kolumna {1}) zawiera wartości {2} niż wartość {3} zadeklarowana dla tej zmiennej w codebooku'
        for iCol, vals in enumerate(df.columns):
            if v > 0:
                print 'minmax checking column '+vals
            # [pl] wersja dokładna, ale wolna [/pl]
            try:
                min_list = []
                for i, val in enumerate(df.iloc[:, iCol]):
                    if t2f(val) < float(cb.iloc[iCol, 8]):
                        min_list.append(str(i+1))
                if len(min_list) != 0:
                    self.msg(eText.format(df.columns[iCol], str(iCol+1), u'mniejsza', u'minimalna', collapse(min_list)), self.msg_mode)
                max_list = []
                for i, val in enumerate(df.iloc[:, iCol]):
                    if t2f(val) > float(cb.iloc[iCol, 9]):
                        max_list.append(str(i+1))
                if len(max_list) != 0:
                    self.msg(eText.format(df.columns[iCol], str(iCol+1), u'większa', u'maksymalna', collapse(max_list)), self.msg_mode)
            except ValueError: # [pl] ignoruj ten błąd przy próbie konwersji tekstu na float przez t2f() [/pl]
                continue
        print 'codebook/dataframe variable range checked.'

    def labels_presence(self, cb, v = None):
        ''' [pl] Czy wszystkim zmiennym przypisano etykiety?; ETYKIETA; kol. 11 [/pl] '''
        if any(p.isnull(cb.iloc[:,10])):
            self.msg(u'Nie wszystkim zmiennym przypisano etykiety', 'report', self.msg_mode)
        print 'codebook/dataframe conditional labels checked.'

    def value_ranges(self, cb, df, v = None):
        ''' [pl] 
        Czy zmienne w ramce danych przyjmują wartości spoza zakresu opisanego 
        w etykietach w codebook-u? 
        ETYKIETA; kol. 11
        [/pl] '''
        for i, name in enumerate(df.columns):
            cLabels = labels_get(cb.iloc[i,10])
            if len(cLabels) != 0:
                if any(df[name].apply(lambda x: str(x) in cLabels.keys()) != False):
                    self.msg('Zmienna {0} przyjmuje wartości spoza zakresu opisanego w etykietach'.format(name), self.msg_mode)
        print 'codebook/dataframe (labelled) value ranges checked.'

    def conditions(self, cb, df, v = None):
        ''' [pl] 
        Czy zmienne, którym w codebook-u przypisano warunek spełniają go? 
        WARUNEK; kol. 12
        [/pl] '''
        ct = conditions_get(cb, df)
        for col in ct.keys():
            has_y = []
            has_n = []
            for i, cell in enumerate(df[col]):
                # [pl] Sprawdź, czy zmienna jest opisana etykietami
                cLabels = labels_get(cb.iloc[i,10])
                if p.notnull(cell) and ct[col][i] == False:
                    has_y.append(i)
                if p.isnull(cell) and ct[col][i] == True:
                    has_n.append(i)
            if len(has_y) != 0:
                self.msg(u'Zmienna {0} ma wartość choć z filtru wynika, że nie powinna; wiersz {1}'.format(col, collapse(has_y)), self.msg_mode)
            if len(has_n) != 0:
                self.msg(u'Zmienna {0} nie ma wartości choć z filtru wynika, że powinna; wiersz {1}'.format(col, collapse(has_n)), self.msg_mode)
        print 'codebook/dataframe conditional variables checked.'

    def test(self, cb, df, v = None):
        self.values(df, v = v)
        self.names(cb, df, v = v)
        self.descriptions(cb, v = v)
        self.types(cb, df, v = v)
        self.scales(cb, df, v = v)
        self.size(cb, df, v = v)
        self.precision(cb, df, v = v)
        self.minmax(cb, df, v = v) # wolne
        self.labels_presence(cb, v = v)
        self.value_ranges(cb, df, v = v)
        self.conditions(cb, df, v = v)
        print 'codebook/dataframe all tests performed.'

# [pl] ------------------------------------------------------------------------- Wywołanie instancji cbdfit:

# [en] Test inputs:

# df = p.read_csv('/media/truecrypt13/mhnatiuk/edudata/test/df.csv', sep = ';', quotechar = '"', encoding='utf-8')
# cb = p.read_csv('/media/truecrypt13/mhnatiuk/edudata/test/codebook.csv', sep = ';', quotechar = '"', encoding='utf-8')
'''
df = p.read_csv('/media/truecrypt13/mhnatiuk/edudata/test/obserwacje_datafile_ok4.csv', sep = ';', quotechar = '"', encoding='utf-8')
cb = p.read_csv('/media/truecrypt13/mhnatiuk/edudata/test/obserwacje_codebook_ok4.csv', sep = ';', quotechar = '"', encoding='utf-8')
test = cbdfit()
test.test(cb, df, v = 1)
for line in test.report:
    print line
'''

# [pl] ------------------------------------------------------------------------- PS. Komunikaty błędów ze skryptu Mateusza:

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
