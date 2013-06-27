# -*- coding: utf-8 -*-
#TO DO: code cleanup: zastanowić się czy te opisy (help_text) powinny być tu
# czy też przenieść je już do template/html
from django.db import models
from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError
from edudata_helpers import is_csv
from django_hstore import hstore
from pandas import DataFrame as psDataFrame
import pandas
import csv
"""
 This is a class representing Research project - an abstract concept of a research that consists of different datasets, materials used to conduct research and so on
"""



class Keyword(models.Model):
    keyword = models.CharField(_(u"Słowo kluczowe"),max_length=100)
    
    def __unicode__(self):
        return self.keyword
    class Meta:
        ordering = ('keyword',)
        abstract = True

class ResearchKeyword(Keyword):
    pass


class DataframeKeyword(Keyword):
    pass

class Team(models.Model):
    name = models.CharField(_(u"Skrót nazwy zespołu"),max_length=12)
    fullname = models.CharField(_(u"Pełna nazwa zespołu"),max_length=100)
    team_members_to_contact = models.CharField(_(u"Członkowie zespołu do kontaktu w sprawie projektu badawczego"),max_length=300)

class ResearchProject(models.Model):
    name = models.CharField(_(u"Nazwa projektu badawczego"),max_length=200)
    subcontractor = models.CharField(_(u"Podwykonawca"),max_length=200)
    team          = models.ForeignKey(Team) ## FOREIGN KEY
    project_start = models.DateField("Początek projektu")                                                                                                                                                                
    project_end   = models.DateField("Koniec projektu")
    research_keywords = models.ManyToManyField(ResearchKeyword) #MANY TO MANY

    def __unicode__(self):
            return(self.name)
    class Meta:
        ordering = ('name',)


class Dataframe(models.Model):
    name = models.CharField(_(u"Nazwa zbioru danych"),help_text=_(u"Nazwa musi być znacząca - dobrze opisująca zbiór danych"),
            max_length=200)    
    def __unicode__(self):
        return self.name

    research_project = models.ForeignKey(ResearchProject)
    observation_unit = models.CharField(_(u"Jednostka obserwacji"),
            help_text=_(u"kto jest bezpośrednim źródłem informacji? (np.stanowisko w instytucji, rodzice o badanych dzieciach, głowa gospodarstwa domowego, itp."),
            max_length=200) 
    # TODO: Jednostka obserwacji: zdecydowac czy ENUM czy TEXT
    population = models.CharField(_(u"Populacja badana"),
            help_text=_(u"Kto/co stanowiło populacje? Uczniowie, studenci, nauczyciele, gospodarstwa domowe, jednostki?"),
            max_length=400)
    sampling_description = models.TextField(_(u"Opis schematu doboru próby"), 
            help_text=_(u"Jak była losowana próba?"))
    sample_size = models.IntegerField(_(u"Liczebność próby"))
    respondent = models.CharField(_(u"Respondent"),
            help_text=_(u"Od kogo zbierano informacje w badaniu?"),max_length=200)
    research_methods = models.CharField(_(u"Metoda badania"),
            help_text=_(u"__DO UZUPEŁNIENIA OPIS__"),max_length = 300)
    collection_method = models.CharField(_(u"Techniki zbierania danych"),
            help_text=_(u"Np. CAWI, CATI, Aplikacja na tablety"),
            max_length = 200)
    keyword = models.ManyToManyField(DataframeKeyword) # MANY TO MANY
    df = models.FileField(_(u"Zbiór danych"),
            upload_to="data/%Y/%m/%d/dataframes",
            max_length=200,
            validators=[is_csv]
    )

    codebook_file = models.FileField(_(u"Codebook"),
            upload_to="data/%Y/%m/%d/codebooks",
            max_length=200,
            validators=[is_csv]
    )
    def validate_codebook(self):
        pass

    def validate_data(self):
        pass

    def save_codebook(self):
        ###
        """
        Save codebook line by line and for each line save also the data 
        that is related to that column to Value table
        """
        
        cb_reader = csv.reader(self.codebook_file, delimiter = ';', quotechar = '"')
        cb_reader.next() ## skip the header of the codebook!
        data_reader =  csv.reader(self.df,delimiter=";",quotechar='"')
        data_header = data_reader.next() ## get this header
        df_rows = [row for row in data_reader]
        pandas_df = psDataFrame(df_rows,columns=data_header)
        df_rows = None
        for nr,row in enumerate(cb_reader):

            #for nr,val in enumerate(row):
            #    print "Elementy", nr, val
            cb = Codebook()
            cb.dataframe = self
            try:
                cb.name, cb.desc_short, cb.desc_long, cb.keywords, cb.type,\
                cb.scale, cb.value_len, cb.precision, cb.min_value,\
                cb.max_value, cb.labels, cb.condition = row
            except ValueError,e:
                print "This should never happen!", len(row)
                raise ValueError,e
            if cb.value_len == '':
                cb.value_len = None
            if cb.precision == '':
                cb.precision = None
            if cb.min_value == '':
                cb.min_value = None
            if cb.max_value == '':
                cb.max_value = None

            assert cb.type in ['liczba rzeczywista', 'liczba całkowita', 'tekst']
            print "Typ kolumny: ",cb.type
            print cb
            cb.save() # save codebook row before saving a column of data
            Value_array = [] # a shitty container, could be done better
            try:
                column = pandas_df[cb.name] # current column - \
                                # should exists if validate() returned True
            except IndexError:
                raise ValidationError, "Codebook and data don't match!"
            for row_nr,val in enumerate(column,start=1): # przelec po kolumnie przy okazji dodajac nr wiersza
                print "Key:", cb.name, cb.pk , "Value:",val 
                value_obj = Value()
                value_obj.set(cb,val,row_nr)
                Value_array.append(value_obj)
            # bulk_create: instead of calling Value.save() method a lot of times
            #    (in fact no of times = no of rows), create one INSERT VALUES()
            print Value_array
            Value.objects.bulk_create(Value_array)
        

    def process_dataframe(self):
        print self.df
        print type(self.df)
        try:
            self.validate_codebook() #TODO @jakosz
        except ValidationError:
            pass
        try:
            self.validate_data() #TODO @jakosz
        except ValidationError:
            pass
        
        self.save_codebook()
        #self.save_df()

    def save(self, *args, **kwargs):
        super(Dataframe, self).save(*args, **kwargs)
        self.process_dataframe()
    class Meta:
        ordering = ('name',)

class Codebook(models.Model):
    name = models.CharField(max_length=200)
    dataframe = models.ForeignKey(Dataframe)
    desc_short = models.CharField(max_length=200)
    desc_long = models.TextField(max_length=200)
    keywords = models.CharField(max_length=200)
    type = models.CharField(max_length=200, choices = \
                (
                    ('int',_(u'liczba całkowita')),
                    ('float', _(u'liczba rzeczywista')),
                    ('string', _(u'tekst')),
                    ('date',_(u'data')),
                    ('TERC',_(u'TERC')),
                    ('weight',_(u'waga'))
                )
            )
    def get_type(self):
        if self.type == u'liczba całkowita':
            return "int"
        elif self.type == u'liczba rzeczywista':
            return "float"
        else:
            return "string"

    scale = models.CharField(max_length = 200, choices = (
                ('dichotomous',_(u'dychotomiczna')),
                ('nominal',_(u'nominalna')),
                ('ordinal',_(u'porządkowa')),
                ('interval',_(u'interwałowa')),
                ('ratio',_(u'ilorazowa')),
                ) ## SEE: codebook FAQ & https://en.wikipedia.org/wiki/Level_of_measurement
            )
    value_len = models.IntegerField(null=True,blank=True) # value length
    precision = models.IntegerField(null=True,blank=True) # only for floating point variables
    min_value = models.FloatField(null=True,blank=True)
    max_value = models.FloatField(null=True,blank=True)
    labels = models.TextField(null=True,blank=True)
    condition = models.CharField(null=True,blank=True,max_length=300)
    def __unicode__(self):
        return self.name
    def __str__(self):
        return ",".join([str(x) for x in ["Codebook: ", 'name',self.name, 'short desc', self.desc_short,\
                'long desc',self.desc_long, 'keywords', self.keywords, \
                '\ntype:',self.type,'scale', self.scale, 'value len', \
                self.value_len, '\tprecision:', self.precision,\
                'min:',self.min_value, '\tmax: ', self.max_value, \
                'labels: ',self.labels, 'condition: ',self.condition]])

class Value(models.Model):
    codebook =  models.ForeignKey(Codebook) ## in fact, index means a codebook\
                                            # column (row in codebook is a \
                                            # column in df
    row = models.IntegerField()
    value_int = models.IntegerField(null=True,blank=True)
    value_float = models.FloatField(null=True,blank=True)
    value_string = models.CharField(null=True,blank=True,max_length=1024)

    
    def set(self,codebook,val, row):
        self.codebook = codebook
        self.set_value(val) 
        self.row = row
    
    def __unicode__(self):
        return self.codebook.name + ':' + self.get_value()
    def get_value(self):
        type = self.codebook.get_type()
        if type == 'int':
            return self.value_int
        elif type == 'float':
            return self.value_float
        elif type == 'string':
            return self.value_string
    def set_value(self, val):
        print "244,Type:",self.codebook.get_type()
        type = self.codebook.get_type()
        if type == 'int':
            self.value_int = val
        elif type == 'float':
            self.value_float = val
        elif type == 'string':
            self.value_string = val

class Product(models.Model):
    product_name = models.CharField(max_length=200,
            choices = (
                (_(u'Narzędzie'),_(u'Narzędzie użyte do zbierania danych')),
                (_(u'Raport merytoryczny'),_(u'Raport merytoryczny')  ),
                (_(u'Raport metodologiczny'),_(u'Raport metodologiczny')),
                (_(u'Inne'),_(u'Inne')),
                )
            )
    dataframe = models.ForeignKey(Dataframe) #FOREIGN KEY
    product_file = models.FileField(
            upload_to = "data/%Y/%m/%d/products",
            max_length=200
            )


