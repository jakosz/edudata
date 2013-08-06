from haystack import indexes
from models import ResearchProject, ResearchKeyword, Codebook


class ResearchProjectIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    name = indexes.CharField(model_attr='name')
    def get_model(self):
        return ResearchProject

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()

class ResearchKeywordIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True,use_template=True)
    keyword = indexes.CharField(model_attr="keyword")

    def get_model(self):
        return ResearchKeyword

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()

class CodebookIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template = True)
    name = indexes.CharField(model_attr="name")
    desc_short = indexes.CharField(model_attr="desc_short")
    desc_long = indexes.CharField(model_attr="desc_long")
    keyword = indexes.CharField(model_attr="keywords")

    def get_model(self):
        return Codebook

