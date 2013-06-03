# -*- encoding: utf-8 -*-

from django.conf.urls import patterns, include, url
#from django.contrib import admin
from django.views.generic import DetailView, ListView
from research_db.models import ResearchProject, research_project


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
	url(r'^research_project/$',
		ListView.as_view(
			queryset=research_project.objects.order_by('-pub_date')[:5],
			context_object_name='latest_research_project_list',
			template_name='analyzer/research_project/index.html')),
	url(r'^research_project/(?P<pk>\d+)/$',
		DetailView.as_view(
			model=research_project,
			template_name='analyzer/research_project/detail.html')),
	url(r'^research_project/show/(?P<researchproject_id>\d+)/$','research_db.views.show'),
)



