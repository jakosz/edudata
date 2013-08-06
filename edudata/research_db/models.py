# -*- coding: utf-8 -*-
#TO DO: code cleanup: zastanowić się czy te opisy (help_text) powinny być tu
# czy też przenieść je już do template/html
from django.db import models
from django.utils.translation import ugettext as _
from django.core.exceptions import ValidationError
from helpers.is_csv import is_csv
from mongodb_datahandler import MongoHandler
from time import time
import markdown
from django.core.urlresolvers import reverse


class Keyword(models.Model):
    keyword = models.CharField(_(u"Słowo kluczowe"),max_length=100)
    
    def __unicode__(self):
        return self.keyword
    class Meta:
        ordering = ('keyword',)
        abstract = True
        verbose_name = _(u"Słowo kluczowe")
        verbose_name_plural = _(u"Słowa kluczowe")
class ResearchKeyword(Keyword):
    def get_absolute_url(self):
        #FIX
        return reverse('researchkeyword.views.details', args=[str(self.id)])
    class Meta:
        verbose_name = _(u"Słowo kluczowe badania")
        verbose_name_plural = _(u"Słowa kluczowe badań")

class DataframeKeyword(Keyword):
    def get_absolute_url(self):
        return reverse('researchkeyword.views.details', args=[str(self.id)])
    class Meta:
        verbose_name = _(u"Słowo kluczowe zbioru danych")
        verbose_name_plural = _(u"Słowa kluczowe zbiorów danych") 

class Team(models.Model):
    name = models.CharField(_(u"Skrót nazwy zespołu"),max_length=12)
    fullname = models.CharField(_(u"Pełna nazwa zespołu"),max_length=100)
    team_members_to_contact = models.CharField(_(u"Członkowie zespołu do kontaktu w sprawie projektu badawczego"),max_length=300)

    def __unicode__(self):
        return self.name
    class Meta:
        verbose_name=_(u"Zespół IBE")
        verbose_name_plural=_(u"Zespoły IBE")


class ResearchProject(models.Model):
    name = models.CharField(_(u"Nazwa projektu badawczego"),max_length=200)
    subcontractor = models.CharField(_(u"Podwykonawca"),max_length=200)
    team          = models.ForeignKey(Team,verbose_name=_(u"Zespół IBE"))## FOREIGN KEY
    person = models.CharField(_(u"Główny badacz"),
            help_text=_(u"Badacz odpowiedzialny za projekt w czasie zbierania danych"), 
            max_length=300)
    project_start = models.DateField("Początek projektu")                                                                                                                                                                
    project_end   = models.DateField("Koniec projektu")
    research_keywords = models.ManyToManyField(ResearchKeyword,verbose_name=_(u"Słowa kluczowe badania")) #MANY TO MANY
    project_description = models.TextField(_("Abstrakt badania"), help_text=_(u"Opisane podstawowe cele badania, pytania badawcze i ewentualne wnioski. Około 200 słów."))
    project_description_html = models.TextField(blank=True)
    citation = models.TextField(_(u"Wzór cytowania"),help_text=_(u"Wymagany format APA") )
    citation_html = models.TextField(blank=True)
    sponsor = models.CharField(_(u"Sponsorzy badania"),help_text=_(u"Kto był sponsorem badania?"),max_length=300)
    
    def __unicode__(self):
            return(self.name)

    def get_absolute_url(self):
        print "WHAT"
        #eturn "project/detail/%i" % self.id
        return reverse('researchproject.detail', args=[str(self.id)])

    def save(self, *args, **kwargs):
        self.project_description_html = markdown.markdown(self.project_description)
        self.citation_html = markdown.markdown(self.citation)
        super(ResearchProject, self).save(*args, **kwargs)
    class Meta:
        ordering = ('name',)
        verbose_name = _(u"Projekt badawczy")
        verbose_name_plural = (u"Projekty badawcze")


class Dataframe(models.Model):
    name = models.CharField(_(u"Nazwa zbioru danych"),help_text=_(u"Nazwa musi być znacząca - dobrze opisująca zbiór danych"),
            max_length=200, unique=True)    
    def __unicode__(self):
        return self.name

    research_project = models.ForeignKey(ResearchProject, verbose_name=_("Projekt badawczy"))
    observation_unit = models.CharField(_(u"Jednostka obserwacji"),
            help_text=_(u"kto jest bezpośrednim źródłem informacji? (np.stanowisko w instytucji, rodzice o badanych dzieciach, głowa gospodarstwa domowego, itp."),
            max_length=200) 
    # TODO: Jednostka obserwacji: zdecydowac czy ENUM czy TEXT
    population = models.CharField(_(u"Populacja badana"),
            help_text=_(u"Kto/co stanowiło populacje? Uczniowie, studenci, nauczyciele, gospodarstwa domowe, jednostki?"),
            max_length=400)
    sampling_description = models.TextField(_(u"Opis schematu doboru próby"),
            help_text=_(u"1. Czy nalezy stosowac wagi i jeśli tak, to jakie.\
            2. Dla badań podłużnych, opis 'retencji' próby: tzw. 'wykruszania' panelu"))
    sampling_description_html = models.TextField(blank=True)
    sample_size = models.IntegerField(_(u"Liczebność próby"))
    response_rate = models.TextField(_(u"Opis response rate w badaniu"), 
            help_text=_(u"Dodatkowo: czy były stosowane próby rezerwowe?"))
    response_rate_html = models.TextField(blank=True)
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
           # validators=[is_csv]
    )

    codebook_file = models.FileField(_(u"Codebook"),
            upload_to="data/%Y/%m/%d/codebooks",
            max_length=200,
            #validators=[is_csv]
    )
    def validate_codebook(self):
        pass

    def validate_data(self):
        pass


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
        
        mongodb = MongoHandler()
        mongodb.process_data(self.name, self.codebook_file, self.df)
        #self.save_df()

    def save(self, *args, **kwargs):
        self.sampling_description_html = markdown.markdown(self.sampling_description)
        self.response_rate_html = markdown.markdown(self.response_rate)
	#t_start  = time()
        super(Dataframe, self).save(*args, **kwargs)
	#t_ms = time()
        self.process_dataframe()
	t_end = time()
	#print "\nTIME: Model save {}, Processing {}".format(t_ms - t_start, t_end - t_ms)
    def get_data(self): # get pandas dataframe
        mongodb = MongoHandler()
        return mongodb.get_dataframe_and_info(self.name)
    def get_csv(self):
        mongodb = MongoHandler()
        return mongodb.get_csv(self.name,";",'.')

    class Meta:
        ordering = ('name',)
        verbose_name=_(u"Zbiór danych")
        verbose_name_plural=_(u"Zbiory danych")
"""
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
        if self.type.decode('utf-8') == u'liczba całkowita':
            return "int"
        elif self.type.decode('utf-8') == u'liczba rzeczywista':
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
    value_int = models.BigIntegerField(null=True,blank=True)
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
        else:
            raise ValueError, _(u"Type doesnt' match any condition")
    def set_value(self, val):
        #print "244,Type:",self.codebook.get_type()
        type = self.codebook.get_type()
        if type == 'int':
            self.value_int = val
        elif type == 'float':
            self.value_float = val
        elif type == 'string':
            self.value_string = val
"""
class Product(models.Model):
    product_name = models.CharField(_(u"Nazwa produktu"),max_length=200,
            choices = (
                (_(u'Narzędzie'),_(u'Narzędzie użyte do zbierania danych')),
                (_(u'Raport merytoryczny'),_(u'Raport merytoryczny')  ),
                (_(u'Raport metodologiczny'),_(u'Raport metodologiczny')),
                (_(u'Inne'),_(u'Inne')),
                )
            )
    dataframe = models.ForeignKey(Dataframe,verbose_name=_(u"Zbiór danych")) #FOREIGN KEY
    product_file = models.FileField(_(u"Plik"),
            upload_to = "data/%Y/%m/%d/products",
            max_length=200
            )
    def __unicode__(self):
        return self.product_name
    class Meta:
        verbose_name=_("Produkt badania")
        verbose_name_plural=_(u"Produkty badania")


