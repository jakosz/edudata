# Create your views here.

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic

from research_db.models import ResearchProject, DataFrame

class IndexView(generic.ListView):
    template_name = 'research_db/index.html'
    context_object_name = 'latest_researchproject_list'

    def get_queryset(self):
        """Return the last five published research projects."""
        return ResearchProject.objects.order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    model = ResearchProject
    template_name = 'research_db/detail.html'


def vote(request, poll_id):
    pass


