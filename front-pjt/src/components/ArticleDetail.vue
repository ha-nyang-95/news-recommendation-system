<template>
  <div class="article-detail" v-if="article">
    <div class="article-header">
      <h1>{{ article.title }}</h1>
      <div class="article-meta">
        <span class="press">{{ article.press }}</span>
        <span class="date">{{ formatDate(article.published_at) }}</span>
        <span class="views">조회수: {{ article.view_count }}</span>
      </div>
    </div>

    <div class="article-content">
      <div class="content-text" v-html="article.content"></div>
      <div class="article-tags">
        <span v-for="tag in article.tags" :key="tag" class="tag">{{ tag }}</span>
      </div>
    </div>

    <!-- 추천 기사 -->
    <div v-if="recommendedArticles.length > 0" class="recommended-articles">
      <h2>추천 기사</h2>
      <div class="recommended-grid">
        <div
          v-for="recommended in recommendedArticles"
          :key="recommended.id"
          class="recommended-card"
          @click="viewArticle(recommended.id)"
        >
          <h3>{{ recommended.title }}</h3>
          <p class="recommended-meta">
            <span>{{ recommended.press }}</span> |
            <span>{{ formatDate(recommended.published_at) }}</span>
          </p>
          <p class="recommended-summary">{{ recommended.summary }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { newsService } from '@/api/newsService';

export default {
  name: 'ArticleDetail',
  data() {
    return {
      article: null,
      recommendedArticles: []
    };
  },
  async created() {
    await this.loadArticle();
  },
  methods: {
    async loadArticle() {
      try {
        const articleId = this.$route.params.id;
        const [article, recommended] = await Promise.all([
          newsService.getArticleDetail(articleId),
          newsService.getRecommendedArticles(articleId)
        ]);
        
        this.article = article;
        this.recommendedArticles = recommended;
      } catch (error) {
        console.error('기사 로딩 실패:', error);
      }
    },
    viewArticle(articleId) {
      this.$router.push(`/article/${articleId}`);
    },
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleDateString('ko-KR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    }
  }
};
</script>

<style scoped>
.article-detail {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
}

.article-header {
  margin-bottom: 40px;
  border-bottom: 2px solid #eee;
  padding-bottom: 20px;
}

.article-header h1 {
  font-size: 2.5em;
  margin-bottom: 20px;
  line-height: 1.4;
  color: #333;
}

.article-meta {
  display: flex;
  gap: 20px;
  color: #666;
  font-size: 0.9em;
}

.article-content {
  margin-bottom: 60px;
}

.content-text {
  font-size: 1.1em;
  line-height: 1.8;
  color: #444;
  margin-bottom: 30px;
}

.article-tags {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.tag {
  padding: 6px 12px;
  background-color: #e9ecef;
  border-radius: 20px;
  font-size: 0.9em;
  color: #495057;
}

.recommended-articles {
  margin-top: 60px;
  padding-top: 40px;
  border-top: 2px solid #eee;
}

.recommended-articles h2 {
  font-size: 1.8em;
  margin-bottom: 30px;
  color: #333;
}

.recommended-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 30px;
}

.recommended-card {
  background: white;
  border: 1px solid #eee;
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s;
}

.recommended-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}

.recommended-card h3 {
  font-size: 1.2em;
  margin-bottom: 15px;
  color: #333;
  line-height: 1.4;
}

.recommended-meta {
  font-size: 0.9em;
  color: #666;
  margin-bottom: 10px;
}

.recommended-summary {
  font-size: 0.95em;
  color: #555;
  line-height: 1.6;
}

@media (max-width: 768px) {
  .article-detail {
    padding: 20px;
  }

  .article-header h1 {
    font-size: 2em;
  }

  .recommended-grid {
    grid-template-columns: 1fr;
  }
}
</style> 