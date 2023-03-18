from django.db import models

# Create your models here


class Article(models.Model):
    article_title = models.CharField(max_length=120, primary_key=True)
    article_url = models.URLField()
    release_time_detected = models.IntegerField()
    article_excerpt = models.CharField(max_length=300)
    article_content = models.CharField(max_length=50000)
    article_class = models.CharField(max_length=150)
    page_urlcode = models.CharField(max_length=100)

    class Meta:
        ordering = ['-release_time_detected']

    # 这一行和其他models文件里的这一行是为了让pycharm识别Model的objects方法
    objects = models.Manager()
