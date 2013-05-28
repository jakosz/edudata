from analyzer.models import Dataframe
from django.contrib import admin

class AnalyzerAdmin(admin.ModelAdmin):
	fields = ['name', 'description','df','codebook','metadata']# 'pub_date']

admin.site.register(Dataframe)
