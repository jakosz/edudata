# -*- encoding: utf-8 -*-
# Create your views here
#from django.template import Context, loader
from analyzer.models import Dataframe
#from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django import forms
###
import csv
import simplejson, json
import random



### Helper functions
"""
Sprobuj zwrocic inta, jak nie, zwroc to, co dostales
"""
def tryint(possible_int):
	try:
		return(int(possible_int))
	except ValueError:
		return(possible_int)
######################################################3
def show(request, dataframe_id):
        df= get_object_or_404(Dataframe, pk=dataframe_id)

	#### Spróbuj otworzyć ramkę danych o którą chodzi (wiadomo z kontekstu wywolania : /analyzer/dataframe/5 )
	try:
		df.df.open()
	except IOError:
		# Nie ma takiej ?
		return render_to_response('analyzer/dataframe/show.html',{
				'dataframe' : df,
				'error_message': "There is no dataframe of this id" ,
		}, context_instance=RequestContext(request))		
	else:
		# OK, odczytaj za pomocą modułu CSV TODO support dla innych delimitrów (user-choice ? )
		reader = csv.reader(df.df, delimiter= ';')
		header = reader.next()
		df.df.close()
		
		# Render to response : po prostu przekaż info z odczytanego pliku (jego header) do wyswietlenie zmiennych
		# TODO tutaj tak naprawdę powinnśmy czytać CODEBOOK a nie header RAMKI i wyświetlać wszystkie ważne info zawarte w nim
		return render_to_response('analyzer/dataframe/show.html',{
				'dataframe': df,
				'header' : header,
		}, context_instance=RequestContext(request))

def plot(request, dataframe_id):
	df = get_object_or_404(Dataframe, pk=dataframe_id)
	try:
		df.df.open()
	except IOError:
                return render_to_response('analyzer/dataframe/plot.html',{
                                'dataframe' : df,
                                'error_message': "There is no dataframe of this id" ,
                }, context_instance=RequestContext(request))
	else:
		"""
		Obiekt choice jest elementem formularza wyświetlanego userowi w widoku SHOW. Kazda zmienna ma swoje id
		choice wskazuje jakie to id . Poniewaz jest to obiekt typu <select> - potrzebna jest lista wyborow.
		To realizuje funkcja getlist
		"""
		variables = request.POST.getlist('choice')
		try:
			variables = [int(var) for var in variables]
		except ValueError:
			return render_to_response('analyzer/datafrme/plot.html',
							{'error_message': "Invalid values passed to the script"},
							context_instance=RequestContext(request))
		if variables:
			reader = csv.reader(df.df, delimiter=";") # TODO : support dla roznych separatorow
			header = reader.next()
			"""
			REMEMBER TODO : jak poradzic sobie nie tylko z pustymi nazwami, ale i z duplikatami, podpowiedz
			UZYJ LISTY
			### !DONE!
			"""
			#subset = dict()
			subset = dict() 
			# Dla kazdej linii w pliku wybierz te kolumny ktore sa okreslone w variables (czyli \
			# zmienne wybrane przez usera. Wartosc z tej kolumny zapisz w slowniku subset \
			# TODO moze wydajniej ??? jest to robic numpy'em : trzeba okreslic ile pamieci \
			# /procesora jest zuzywane przy duzych ramkach danych.
			for line in reader:
				for column in variables:
					try:
						subset[column][1].append(tryint(line[column]))
						#subset[column][1].append(random.randint(-1000,1000))
					except KeyError:
						subset[column] = [ header[column], [] ]
						subset[column][1].append(tryint(line[column]))
						#subset[column][1].append(random.randint(-1000, 1000))
			# Przygotuj kontener na osobnego JSONA dla kazdej zmiennej ( TODO sprawdzic czy wydajniej \
			# jest miec jednego jebutnego JSONA, czy też tak jak jest teraz. Intuicyjnie: tak jak teraz
			subset_json = {}
			for var, val in subset.iteritems():
				subset_json[var] = [val[0], json.dumps(val[1]) ]
			## do renderowania zrzuc df ( bo nazwa ramki danych itp. ale calego nie ma sensu) \
			# oraz JSONA
			return render_to_response('analyzer/dataframe/plot.html',
							{ 'dataframe' : df,
							  'columns' : subset_json, },
							context_instance=RequestContext(request))
		else:
			return render_to_response('analyzer/dataframe/plot.html',
                	                                        { 'dataframe' : df,
								  'error_message': "No variables passed to plot",},
                                	                        context_instance=RequestContext(request))



