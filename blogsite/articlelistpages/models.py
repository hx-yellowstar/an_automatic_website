from django.db import models

# Create your models here.

class Article(models.Model):
    title = models.CharField(max_length=150)
    sourceurl = models.URLField(primary_key=True)
    articlecontent = models.CharField(max_length=50000)
