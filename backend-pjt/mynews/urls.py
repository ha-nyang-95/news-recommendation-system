# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NewsListView, NewsDetailView, DashboardMockView, RelatedNewsView, RecommendedArticlesView, search_news, suggest_search, get_related_keywords, NewsViewSet

router = DefaultRouter()
router.register(r'news', NewsViewSet, basename='news')

urlpatterns = [
    path('', NewsListView.as_view(), name='news-list'),
    path('<int:id>/', NewsDetailView.as_view(), name='news-detail'),
    path('<int:id>/related/', RelatedNewsView.as_view(), name='related-news'),  # 관련 뉴스 경로 추가
    path('dashboard/', DashboardMockView.as_view(), name='dashboard-mock'),
    path("<int:id>/recommend/", RecommendedArticlesView.as_view()),
    path('search/', search_news, name='news-search'),  # 이 엔드포인트만 사용
    path('suggest/', suggest_search, name='news-suggest'),
    path('related-keywords/', get_related_keywords, name='related-keywords'),
    path('', include(router.urls)),
]