import datetime
from haystack import indexes
from article.models import Article

class ArticleIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        return Article

    def index_queryset(self, using=None):
        print('process query')
        return self.get_model().objects.all()