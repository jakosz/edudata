# -*- encoding: utf-8 -*-

from django.conf.urls import patterns, include, url
#from django.contrib import admin
from django.views.generic import DetailView, ListView
from research_db.models import ResearchProject, Dataframe


"""
Kiedy uzytkownik wprowadza adres ktory zaczyna sie od 
www.EXAMPLE.com/research_db/, skrypt idzie do appki Research_db czyli 
do tego ( . ) folderu i probuje dopasowac nasteujace wyrazenia regularne 
do widokow:
	* index - lista wszystkich projektu badawczego
	* detail - szczegoly na temat projektu badawczego
"""

urlpatterns = patterns('',
	url(r'^project/$',
		ListView.as_view(
			queryset=ResearchProject.objects.order_by('-pub_date')[:5],
			context_object_name='latest_research_project_list',
			template_name='research_db/index.html')),
	url(r'^project/(?P<pk>\d+)/$',
		DetailView.as_view(
			model=ResearchProject,
			template_name='research_db/detail.html')),
)



