import datetime
from haystack import indexes
from models import Dataframe, ResearchProject, ResearchKeyword


class ResearchProjectIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    name = indexes.CharField(model_attr='name')
    def get_model(self):
        return ResearchProject

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        #return self.get_model().objects.filter(pub_date__lte=datetime.datetime.now())
        return self.get_model().objects.all()

class ResearchKeywordIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True,use_template=True)
    keyword = indexes.CharField(model_attr="keyword")

    def get_model(self):
        return ResearchKeyword
