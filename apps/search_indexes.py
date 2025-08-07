from haystack import indexes
from apps.models import Release



class ReleaseIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.EdgeNgramField(document = True, use_template = True)

    Bundle_Description = indexes.CharField(model_attr='Bundle_Description', null=True)

    authors = indexes.MultiValueField(null=True)

    app = indexes.CharField(model_attr='app')

    short_title = indexes.CharField(model_attr='short_title', null=True)

    Bundle_Name = indexes.CharField()

    def get_model(self):
        return Release

    def prepare_authors(self, obj):
        return [author.id for author in obj.authors.all()]

    def prepare_app(self, obj):
        return obj.app
