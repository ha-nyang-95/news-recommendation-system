from rest_framework import serializers
from .models import NewsArticle
import json

# serializers.py
class NewsArticleSerializer(serializers.ModelSerializer): 
    embedding = serializers.SerializerMethodField()
    class Meta:
        model = NewsArticle
        fields = ['id', 'title', 'writer', 'write_date', 'category', 'content', 'url', 'embedding', 'keywords']

    def get_embedding(self, obj):
        try:
            if isinstance(obj.embedding, str):
                return json.loads(obj.embedding)  # 문자열이면 리스트로 변환
            return obj.embedding  # 이미 리스트면 그대로
        except Exception:
            return []