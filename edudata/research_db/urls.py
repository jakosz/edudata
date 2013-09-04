# -*- encoding: utf-8 -*-

from django.conf.urls import patterns, include, url
#from django.contrib import admin
from django.views.generic import DetailView, ListView
from research_db.views import *
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
        url(r'^$', ResearchProjectIndex.as_view(),name="list"),
	url(r'^project/$',
		ResearchProjectIndex.as_view(), name= "list"),
	url(r'^project/(?P<pk>\d+)/$', ResearchProjectDetail.as_view(), name = "researchproject.detail"),
        url(r'^dataframe_basicinfo/(?P<pk>\d+)/$', dataframe_basicinfo, name="dataframe_basicinfo"),
        url(r'^get_json_var/(?P<var_id>\d+)/$', get_json_var, name="get_json_var"),

	url(r'^analyze_var/(?P<var_id>\d+)/$', analyze_var, name = "analyze_var"),
	url(r'^histogram/(?P<var_id>\d+)/$', get_histogram, name = "get_histogram"),
)



