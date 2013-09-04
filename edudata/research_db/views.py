# Create your views here.

import json
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views import generic
from research_db.decorators import *
from research_db.models import ResearchProject, Dataframe,Codebook
from research_db.mongodb_datahandler import MongoHandler
from haystack.views import SearchView
from analyzer import Analyzer


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
    def html_cell(content):
        return "<td>"+unicode(content)+"</td>"
    for key,val in column.iteritems():
	if key != u'_id':
            row_html += html_cell(val)
    return row_html

def theader(column_name):
	return "<th>"+unicode(column_name)+"</th>"

@html_bstrap_table
def render_codebook_info(codebook_info):
    table_html = ""
    first = True
    for key,value in codebook_info.iteritems():
	print key,
	if key != u'_id':
	    if first==True:
	        table_html += "".join([theader(key) for key,val in value.iteritems() ] )
	    table_html += render_codebook_row(value)
	    first=False
	else:
	    pass
    return table_html


def dataframe_basicinfo(request, pk):
    dataframe = get_object_or_404(Dataframe, pk=pk)
    paginator = Paginator(dataframe.codebook_set.all(),25)
    page = request.GET.get('page')
    try:
        variables = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        variables = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        variables = paginator.page(paginator.num_pages)

    return render(request,'research_db/dataframe/basicinfo.html', {"variables": variables})
    #data_and_info = dataframe.get_data()
    #psDf = data_and_info['df']
    #codebook_info = data_and_info['info']

    #summary_html = psDf.describe().to_html(classes=('table','table-stripped','table-bordered'))
    #return render(request, 'research_db/dataframe/basicinfo.html',
    #        {'dataframe': dataframe, 'codebook_info': render_codebook_info(codebook_info),
    #            'summary_html':summary_html})


def get_json_var(context,var_id):
    codebook_var = Codebook.objects.get(pk=var_id)
    mh  = MongoHandler()
    cursor = mh.db.dataframes.find({'df_name':codebook_var.dataframe.name, 'name':codebook_var.name})   
    var = cursor.next()
    to_json= var['data']
    print "Sprawdzam czy context jest True",
    print context != ''
    if context != '':
        return HttpResponse(json.dumps(to_json), mimetype="application/json")
    else:
        return json.dumps(to_json)

def analyze_var(contex,var_id):
    json_var = get_json_var('',var_id)
    analyzer = Analyzer(json_var)
    hist_data = analyzer.hist_data()
    return render(request,'research_db/dataframe/hist_data.html', {"histogram": hist_data})

def get_histogram(context,var_id):
    json_var = get_json_var('',var_id)
    analyzer = Analyzer(json_var)
    return HttpResponse(analyzer.histogram(),mimetype="image/png")




