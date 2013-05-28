# -*- encoding: utf-8 -*-

from django.conf.urls import patterns, include, url
#from django.contrib import admin
from django.views.generic import DetailView, ListView
from analyzer.models import Dataframe


"""
Kiedy uzytkownik wprowadza adres ktory zaczyna sie od www.EXAMPLE.com/analyzer/, skrypt idzie do appki ANALYZER czyli do tego ( . ) folderu i probuje dopasowac nasteujace wyrazenia regularne do widokow:
	* index - lista wszystkich ramek danych
	* detail - szczegoly na temat ramki danych
	* show - pokaz zmienne
	* plot - wyswietl wyniki "analizy" - w tej chwili histogramy zaznaczonych zmiennych.
"""
### TODO : zastanowic się nad tym, jak by to miało wyglądać w przyszłości: czy te modele są dostosowane do tego jak będziemy ich uzywać
### pewnie warto oddzielic opis ramki danych, wybieranie analiz od ich wyswietlania itp. To są na razie wild guessy

urlpatterns = patterns('',
	url(r'^dataframe/$',
		ListView.as_view(
			queryset=Dataframe.objects.order_by('-pub_date')[:5],
			context_object_name='latest_dataframe_list',
			template_name='analyzer/dataframe/index.html')),
	url(r'^dataframe/(?P<pk>\d+)/$',
		DetailView.as_view(
			model=Dataframe,
			template_name='analyzer/dataframe/detail.html')),
	url(r'^dataframe/show/(?P<dataframe_id>\d+)/$','analyzer.views.show'),
	url(r'^dataframe/plot/(?P<dataframe_id>\d+)/$','analyzer.views.plot'),
)



