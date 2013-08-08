# Create your views here.

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from research_db.decorators import *
from research_db.models import ResearchProject, Dataframe

class ResearchProjectIndex(generic.ListView):
    print "RP INDEX"
    template_name = 'research_db/researchproject/index.html'
    context_object_name = 'researchproject_list'
    def get_queryset(self):
        """Return all research projects."""
        print ResearchProject.objects.all()
        return ResearchProject.objects.all()


class ResearchProjectDetail(generic.DetailView):
    model = ResearchProject
    template_name = 'research_db/researchproject/detail.html'



@html_row
def render_codebook_row(column):
    row_html = ""
    print "!!!!!",column
    def html_cell(content):
        return "<td>"+content+"</td>"
    for key,val in column.iteritems():
        row_html += html_cell(val)
    return row_html

@html_bstrap_table
def render_codebook_info(codebook_info):
    table_html = ""
    for key,value in codebook_info.iteritems():
        table_html += render_codebook_row(value)
    return table_html


def dataframe_basicinfo(request, pk):
    dataframe = get_object_or_404(Dataframe, pk=pk)
    data_and_info = dataframe.get_data()
    psDf = data_and_info['df']
    codebook_info = data_and_info['info']

    summary_html = psDf.describe().to_html(classes=('table','table-stripped','table-bordered'))
    return render(request, 'research_db/dataframe/basicinfo.html',
            {'dataframe': dataframe, 'codebook_info': render_codebook_info(codebook_info),
                'summary_html':summary_html})

