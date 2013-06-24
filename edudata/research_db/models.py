# -*- coding: utf-8 -*-
#TO DO: code cleanup: zastanowić się czy te opisy (help_text) powinny być tu
# czy też przenieść je już do template/html
import datetime
from django.utils import timezone
from django.db import models
from django.utils.translation import ugettext as _
from edudata_helpers import is_csv
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

    class Meta:
        ordering = ('name',)

class Codebook(models.Model):
    name = models.CharField(max_length=200)
    dataframe = models.ForeignKey(Dataframe)
    desc_short = models.CharField(max_length=200)
    desc_long = models.CharField(max_length=200)
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
    scale = models.CharField(max_length = 200, choices = (
                ('dichotomous',_(u'dychotomiczna')),
                ('nominal',_(u'nominalna')),
                ('ordinal',_(u'porządkowa')),
                ('interval',_(u'interwałowa')),
                ('ratio',_(u'ilorazowa')),
                ) ## SEE: codebook FAQ & https://en.wikipedia.org/wiki/Level_of_measurement
            )
    value_len = models.IntegerField() # value length
    precision = models.IntegerField() # only for floating point variables
    min_value = models.DecimalField(decimal_places = 15, max_digits = 15)
    max_value = models.DecimalField(decimal_places = 15, max_digits = 15)
    labels = models.CharField(max_length=300)
    condition = models.CharField(max_length=300)


class Values(models.Model):
    codebook =  models.ForeignKey(Codebook)
    row_order = models.IntegerField()
    value_int = models.IntegerField()
    value_float = models.DecimalField(decimal_places = 15, max_digits = 15)
    value_string = models.TextField()
    

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


