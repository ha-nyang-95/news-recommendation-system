# mynews/views.py
from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from .mocking import dashboard_mock
from .models import NewsArticle
from .serializers import NewsArticleSerializer
from rest_framework.decorators import api_view, action
from .elasticsearch_config import es_client
from django.conf import settings
from elasticsearch import Elasticsearch
from datetime import datetime
import logging
from .sync_script import sync_to_elasticsearch

# 로깅 설정
logger = logging.getLogger(__name__)

# Elasticsearch 클라이언트
es_client = Elasticsearch(
    hosts=[settings.ELASTICSEARCH_HOST],
    basic_auth=(settings.ELASTICSEARCH_USER, settings.ELASTICSEARCH_PASSWORD)
)

class DashboardMockView(APIView):
    def get(self, request):
        dashboard_mock
        return Response(dashboard_mock)

# your_app/views.py
from django.views import View
from django.http import JsonResponse
from .models import News
from django.core.paginator import Paginator
from django.db.models import Q
from django.db import connection


# mynews/views.py
from django.views import View
from django.http import JsonResponse
from .models import NewsArticle  # News 대신 NewsArticle 사용
from django.core.paginator import Paginator

class RecommendedArticlesView(APIView):
    def get(self, request, id):
        try:
            current = NewsArticle.objects.get(id=id)

            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT id, title, content, category, keywords, write_date, writer, url, embedding <-> %s AS similarity
                    FROM news_article
                    WHERE id != %s
                    ORDER BY similarity ASC
                    LIMIT 5
                """, [current.embedding, current.id])
                rows = cursor.fetchall()
            
            result = [
                {
                    'id': news[0],
                    'title': news[1],
                    'content': news[2],
                    'category': news[3],
                    'keywords': news[4] or [],
                    'write_date': news[5] or '',
                    'writer': news[6] or '알 수 없음',
                    'url': news[7] or '',
                } for news in rows
            ]
            return Response(result)

        except NewsArticle.DoesNotExist:
            return Response({"error": "해당 기사가 없습니다."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

class NewsListView(View):
    def get(self, request):
        try:
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', 10))
            sort_by = request.GET.get('sort_by', 'latest')
            category = request.GET.get('category', None)

            news_qs = NewsArticle.objects.all()  # NewsArticle로 변경

            if category:
                news_qs = news_qs.filter(category=category)

            if sort_by == 'latest':
                news_qs = news_qs.order_by('-write_date')
            elif sort_by == 'oldest':
                news_qs = news_qs.order_by('write_date')

            paginator = Paginator(news_qs, page_size)
            page_obj = paginator.get_page(page)

            news_data = [
                {
                    'id': news.id,
                    'title': news.title,
                    'content': news.content,
                    'category': news.category,
                    'keywords': news.keywords if news.keywords else [],  # ArrayField 처리
                    'write_date': news.write_date.isoformat() if news.write_date else '',
                    'writer': news.writer or '알 수 없음',
                    'url': news.url or '',
                    'article_interaction': {'likes': 0, 'read': 0},  # NewsArticle에 없으므로 기본값 설정
                }
                for news in page_obj
            ]

            response = {
                'news': news_data,
                'total_pages': paginator.num_pages,
                'current_page': page_obj.number,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
            }
            return JsonResponse(response)
        except Exception as e:
            return JsonResponse({'error': f'서버 오류: {str(e)}'}, status=500)

class NewsDetailView(generics.RetrieveAPIView):
    queryset = NewsArticle.objects.all()
    serializer_class = NewsArticleSerializer
    lookup_field = 'id'  # 또는 'pk'도 가능

# views.py
from django.views import View
from django.http import JsonResponse
from .models import News  # News 모델을 임포트 (모델 이름은 가정)
from django.core.exceptions import ObjectDoesNotExist

# mynews/views.py
from django.views import View
from django.http import JsonResponse
from .models import NewsArticle  # News 대신 NewsArticle 사용
from django.core.exceptions import ObjectDoesNotExist

class RelatedNewsView(View):
    def get(self, request, id):
        try:
            current_news = NewsArticle.objects.get(id=id)  # NewsArticle로 변경
            related_news = NewsArticle.objects.filter(category=current_news.category).exclude(id=id)[:3]

            related_news_data = [
                {
                    'id': news.id,
                    'title': news.title,
                    'content': news.content,
                    'category': news.category,
                    'keywords': news.keywords if news.keywords else [],
                    'write_date': news.write_date.isoformat() if news.write_date else '',
                    'writer': news.writer or '알 수 없음',
                    'url': news.url or '',
                    'article_interaction': {'likes': 0, 'read': 0},  # 기본값 설정
                }
                for news in related_news
            ]

            return JsonResponse(related_news_data, safe=False)
        except ObjectDoesNotExist:
            return JsonResponse({'error': '뉴스를 찾을 수 없습니다.'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@api_view(['GET'])
def search_news(request):
    """
    뉴스 기사 검색 API
    """
    query = request.GET.get('q', '')
    category = request.GET.get('category')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    sort_by = request.GET.get('sort', 'relevance')  # 정렬 기준
    page = int(request.GET.get('page', 1))
    size = int(request.GET.get('size', 10))
    
    # 검색 쿼리 구성
    if query:
        must_query = [{
            "multi_match": {
                "query": query,
                "fields": ["title^3", "content", "writer"],
                "type": "best_fields",
                "minimum_should_match": "50%"
            }
        }]
    else:
        must_query = [{"match_all": {}}]
    
    search_query = {
        "bool": {
            "must": must_query,
            "filter": []
        }
    }
    
    # 카테고리 필터 추가
    if category:
        search_query["bool"]["filter"].append({"term": {"category": category}})
    
    # 날짜 범위 필터 추가
    if start_date or end_date:
        date_filter = {"range": {"write_date": {}}}
        if start_date:
            date_filter["range"]["write_date"]["gte"] = start_date
        if end_date:
            date_filter["range"]["write_date"]["lte"] = end_date
        search_query["bool"]["filter"].append(date_filter)
    
    # 정렬 기준 설정
    sort_options = {
        "relevance": [{"_score": {"order": "desc"}}, {"write_date": {"order": "desc"}}],
        "latest": [{"write_date": {"order": "desc"}}],
        "oldest": [{"write_date": {"order": "asc"}}],
        "title_asc": [{"title.keyword": {"order": "asc"}}],
        "title_desc": [{"title.keyword": {"order": "desc"}}]
    }
    
    sort = sort_options.get(sort_by, sort_options["relevance"])
    
    # 검색 실행
    response = es_client.search(
        index="news",
        body={
            "query": search_query,
            "sort": sort,
            "from": (page - 1) * size,
            "size": size,
            "highlight": {
                "fields": {
                    "title": {},
                    "content": {
                        "fragment_size": 150,
                        "number_of_fragments": 3
                    }
                }
            }
        }
    )
    
    # 검색 결과 가공
    results = []
    for hit in response['hits']['hits']:
        result = {
            'id': hit['_id'],
            'title': hit['_source']['title'],
            'content': hit['_source']['content'],
            'writer': hit['_source']['writer'],
            'category': hit['_source']['category'],
            'write_date': hit['_source']['write_date'],
            'url': hit['_source']['url'],
            'keywords': hit['_source'].get('keywords', []),
            'score': hit['_score']
        }
        
        # 하이라이트 처리
        if 'highlight' in hit:
            if 'title' in hit['highlight']:
                result['title_highlight'] = hit['highlight']['title'][0]
            if 'content' in hit['highlight']:
                result['content_highlight'] = hit['highlight']['content']
        
        results.append(result)
    
    return JsonResponse({
        "results": results,
        "total": response['hits']['total']['value'],
        "size": size,
        "page": page,
    })

@api_view(['GET'])
def suggest_search(request):
    """
    검색어 자동완성 API
    """
    query = request.GET.get('q', '')
    if not query:
        return Response([])

    try:
        # Elasticsearch suggest 쿼리
        suggest_query = {
            "suggest": {
                "title_suggest": {
                    "prefix": query,
                    "completion": {
                        "field": "title.suggest",
                        "size": 5,
                        "skip_duplicates": True
                    }
                },
                "keyword_suggest": {
                    "prefix": query,
                    "completion": {
                        "field": "keywords.suggest",
                        "size": 5,
                        "skip_duplicates": True
                    }
                }
            }
        }

        # Elasticsearch suggest 요청
        response = es_client.search(
            index="news",
            body=suggest_query
        )

        # 결과 가공
        suggestions = set()
        
        # 제목 자동완성 결과
        if 'suggest' in response and 'title_suggest' in response['suggest']:
            for option in response['suggest']['title_suggest'][0]['options']:
                suggestions.add(option['text'])

        # 키워드 자동완성 결과
        if 'suggest' in response and 'keyword_suggest' in response['suggest']:
            for option in response['suggest']['keyword_suggest'][0]['options']:
                suggestions.add(option['text'])

        return Response(list(suggestions))

    except Exception as e:
        return Response({"error": str(e)}, status=500)

@api_view(['GET'])
def get_related_keywords(request):
    """
    연관 키워드 추천 API
    """
    query = request.GET.get('q', '')
    if not query:
        return Response([])

    try:
        # Elasticsearch more_like_this 쿼리
        search_query = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "multi_match": {
                                "query": query,
                                "fields": ["title^3", "content", "keywords"]
                            }
                        }
                    ]
                }
            },
            "aggs": {
                "related_keywords": {
                    "terms": {
                        "field": "keywords",
                        "size": 10,
                        "min_doc_count": 2
                    }
                }
            },
            "size": 0
        }

        # Elasticsearch 검색 실행
        response = es_client.search(
            index="news",
            body=search_query
        )

        # 결과 가공
        related_keywords = []
        if 'aggregations' in response and 'related_keywords' in response['aggregations']:
            buckets = response['aggregations']['related_keywords']['buckets']
            related_keywords = [bucket['key'] for bucket in buckets if bucket['key'] != query]

        return Response(related_keywords)

    except Exception as e:
        return Response({"error": str(e)}, status=500)

class NewsViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['get'])
    def search(self, request):
        """뉴스 검색 API"""
        try:
            # 검색 파라미터 추출
            query = request.query_params.get('q', '')
            category = request.query_params.get('category', '')
            writer = request.query_params.get('writer', '')
            start_date = request.query_params.get('start_date', '')
            end_date = request.query_params.get('end_date', '')
            sort_by = request.query_params.get('sort', 'relevance')
            page = int(request.query_params.get('page', 1))
            size = int(request.query_params.get('size', 10))

            # 검색 쿼리 구성
            must_conditions = []
            
            if query:
                must_conditions.append({
                    "multi_match": {
                        "query": query,
                        "fields": ["title^3", "content", "keywords^2"],
                        "type": "best_fields",
                        "operator": "and"
                    }
                })
            
            if category:
                must_conditions.append({"term": {"category": category}})
            
            if writer:
                must_conditions.append({"term": {"writer.keyword": writer}})
            
            if start_date or end_date:
                date_range = {}
                if start_date:
                    date_range["gte"] = start_date
                if end_date:
                    date_range["lte"] = end_date
                must_conditions.append({"range": {"write_date": date_range}})

            # 정렬 설정
            sort_config = []
            if sort_by == 'relevance':
                sort_config = ["_score"]
            elif sort_by == 'latest':
                sort_config = [{"write_date": "desc"}]
            elif sort_by == 'oldest':
                sort_config = [{"write_date": "asc"}]
            elif sort_by == 'title_asc':
                sort_config = [{"title.keyword": "asc"}]
            elif sort_by == 'title_desc':
                sort_config = [{"title.keyword": "desc"}]

            # 검색 실행
            search_body = {
                "query": {
                    "bool": {
                        "must": must_conditions,
                        "filter": [{"term": {"is_active": True}}]
                    }
                },
                "sort": sort_config,
                "from": (page - 1) * size,
                "size": size,
                "highlight": {
                    "fields": {
                        "title": {},
                        "content": {
                            "fragment_size": 150,
                            "number_of_fragments": 3
                        }
                    }
                },
                "aggs": {
                    "category_stats": {
                        "terms": {
                            "field": "category",
                            "size": 10
                        }
                    }
                }
            }

            # 검색 실행
            response = es_client.search(
                index="news",
                body=search_body
            )

            # 검색 결과 처리
            hits = response['hits']['hits']
            total = response['hits']['total']['value']
            aggregations = response.get('aggregations', {})

            # 검색 결과 포맷팅
            results = []
            for hit in hits:
                result = hit['_source']
                result['id'] = hit['_id']
                result['score'] = hit['_score']
                
                # 하이라이팅 처리
                if 'highlight' in hit:
                    if 'title' in hit['highlight']:
                        result['title_highlight'] = hit['highlight']['title'][0]
                    if 'content' in hit['highlight']:
                        result['content_highlight'] = ' ... '.join(hit['highlight']['content'])

                results.append(result)

            # 응답 구성
            return Response({
                'total': total,
                'page': page,
                'size': size,
                'results': results,
                'aggregations': aggregations
            })

        except Exception as e:
            logger.error(f"검색 중 오류 발생: {str(e)}")
            return Response(
                {'error': '검색 중 오류가 발생했습니다.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def suggest(self, request):
        """검색어 추천 API"""
        try:
            query = request.query_params.get('q', '')
            if not query:
                return Response([])

            # 자동완성 쿼리
            suggest_body = {
                "suggest": {
                    "title_suggest": {
                        "prefix": query,
                        "completion": {
                            "field": "title.suggest",
                            "size": 5,
                            "skip_duplicates": True
                        }
                    },
                    "keyword_suggest": {
                        "prefix": query,
                        "completion": {
                            "field": "keywords.suggest",
                            "size": 5,
                            "skip_duplicates": True
                        }
                    }
                }
            }

            response = es_client.search(
                index="news",
                body=suggest_body
            )

            # 추천 결과 처리
            suggestions = set()
            for suggest_type in ['title_suggest', 'keyword_suggest']:
                for option in response['suggest'][suggest_type][0]['options']:
                    suggestions.add(option['text'])

            return Response(list(suggestions))

        except Exception as e:
            logger.error(f"추천 중 오류 발생: {str(e)}")
            return Response(
                {'error': '추천 중 오류가 발생했습니다.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def increment_view(self, request, pk=None):
        """조회수 증가 API"""
        try:
            # Elasticsearch 문서 업데이트
            es_client.update(
                index="news",
                id=pk,
                body={
                    "script": {
                        "source": "ctx._source.view_count += 1",
                        "lang": "painless"
                    }
                }
            )

            # PostgreSQL 업데이트
            article = NewsArticle.objects.get(id=pk)
            article.view_count += 1
            article.save()

            return Response({'status': 'success'})

        except Exception as e:
            logger.error(f"조회수 증가 중 오류 발생: {str(e)}")
            return Response(
                {'error': '조회수 증가 중 오류가 발생했습니다.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )