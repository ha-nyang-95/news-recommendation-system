import json
from django.db import models
from django.contrib.postgres.fields import ArrayField


class News(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    category = models.CharField(max_length=100)
    keywords = models.JSONField(default=list)  # 키워드 리스트
    write_date = models.DateTimeField(auto_now_add=True)
    writer = models.CharField(max_length=100)
    url = models.URLField(blank=True, null=True)
    article_interaction = models.JSONField(default=dict)  # {likes: 0, read: 0} 형태
    class Meta:
        db_table = 'news_article'
        managed = False
    def __str__(self):
        return self.title

class NewsArticle(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.TextField()
    writer = models.TextField()
    write_date = models.DateTimeField()
    category = models.TextField()
    content = models.TextField()
    url = models.TextField(unique=True)
    embedding = ArrayField(models.FloatField(), null=True, blank=True)
    keywords = ArrayField(models.TextField(), default=list)
    class Meta:
        db_table = 'news_article'
        managed = False
    def __str__(self):
        return self.title
