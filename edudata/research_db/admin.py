from django.contrib import admin
from django.db import models
import research_db.models

from nested_inlines.admin import NestedModelAdmin, NestedStackedInline, NestedTabularInline

from pagedown.widgets import AdminPagedownWidget

class NestedProductInline(NestedTabularInline):
    model = research_db.models.Product
    extra = 3
class DataframeInline(NestedStackedInline):
    formfield_overrides = {
            models.TextField: {
                'widget':AdminPagedownWidget},
            }
    model = research_db.models.Dataframe
    inlines = [NestedProductInline]
    extra =1
    exclude = ('sampling_description_html',)

class DataframeAdmin(admin.ModelAdmin):
    formfield_overrides = {
            models.TextField: {'widget':AdminPagedownWidget},
            }
    exclude = ('sampling_description_html',)

class ResearchProjectAdmin(NestedModelAdmin):
    inlines = [DataframeInline]
    formfield_overrides = {
            models.TextField: {'widget':AdminPagedownWidget},
            }
    exclude = ('sampling_description_html',)

admin.site.register(research_db.models.ResearchProject, ResearchProjectAdmin)
admin.site.register(research_db.models.Dataframe, DataframeAdmin)
admin.site.register(research_db.models.Product)
admin.site.register(research_db.models.ResearchKeyword)
admin.site.register(research_db.models.DataframeKeyword)
admin.site.register(research_db.models.Team)

