from haystack import indexes
from apps.models import App


class AppIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.EdgeNgramField(document = True, use_template = True)
    Bundle_Name = indexes.CharField(model_attr='Bundle_Name',null=True)

    categories = indexes.MultiValueField(model_attr = 'categories',null=True)

    downloads = indexes.IntegerField(model_attr = 'downloads',null = True)
    stars =indexes.IntegerField(model_attr = 'stars',null = True)


    def get_model(self):
        return App

    # def prepare_authors(self, obj):
    #     return [author.id for author in obj.authors.all()]

    # short_title = indexes.CharField(model_attr='short_title', null=True)
    # has_releases = indexes.BooleanField(model_attr='has_releases', null=True)
    # authors = indexes.MultiValueField(model_attr='authors', null=True)
    # Bundle_Description = indexes.CharField(model_attr = 'Bundle_Description',null=True)

    def prepare_tags(self, obj):
        return [tag.id for tag in obj.categories.all()]

