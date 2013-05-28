# -*- encoding: utf-8 -*-

from django.conf.urls import patterns, include, url
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

###
# Aktywuj panel admina / Enable administrative panel. 
# ? Co dokladnie robi ta fun
###
admin.autodiscover()

urlpatterns = patterns('',
	#url(r'^polls/', include('polls.urls')),
	url(r'^analyzer/', include('analyzer.urls')),
	url(r'^admin/', include(admin.site.urls)),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

"""
Urlpatterns przekierowuja na odpowiednie VIEWS kiedy uzytkownik zazada adresu pasujacego do wyrazenia regularnego
+ static daje link do plikow statycznych (pliki *.js, *.css), które docelowo mogą i powinny być na osobnym serwerze: eliminacja cross-site sriptingu
"""


