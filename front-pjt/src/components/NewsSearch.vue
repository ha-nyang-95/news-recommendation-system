<template>
  <div class="news-search">
    <div class="search-container">
      <div class="search-box">
        <input
          type="text"
          v-model="searchQuery"
          @input="handleInput"
          @keyup.enter="search"
          placeholder="검색어를 입력하세요"
          class="search-input"
        />
        <button @click="search" class="search-button">검색</button>
      </div>
      
      <!-- 검색어 추천 -->
      <div v-if="suggestions.length > 0" class="suggestions">
        <div
          v-for="suggestion in suggestions"
          :key="suggestion"
          @click="selectSuggestion(suggestion)"
          class="suggestion-item"
        >
          {{ suggestion }}
        </div>
      </div>

      <!-- 연관 키워드 -->
      <div v-if="relatedKeywords.length > 0" class="related-keywords">
        <h3>연관 키워드</h3>
        <div class="keyword-tags">
          <span
            v-for="keyword in relatedKeywords"
            :key="keyword"
            @click="searchWithKeyword(keyword)"
            class="keyword-tag"
          >
            {{ keyword }}
          </span>
        </div>
      </div>
    </div>

    <!-- 검색 결과 -->
    <div v-if="searchResults.length > 0" class="search-results">
      <div v-for="article in searchResults" :key="article.id" class="article-card">
        <h2 @click="viewArticle(article.id)">{{ article.title }}</h2>
        <p class="article-meta">
          <span>{{ article.press }}</span> |
          <span>{{ formatDate(article.published_at) }}</span> |
          <span>조회수: {{ article.view_count }}</span>
        </p>
        <p class="article-summary">{{ article.summary }}</p>
        <div class="article-tags">
          <span v-for="tag in article.tags" :key="tag" class="tag">{{ tag }}</span>
        </div>
      </div>
    </div>

    <!-- 페이지네이션 -->
    <div v-if="totalPages > 1" class="pagination">
      <button
        :disabled="currentPage === 1"
        @click="changePage(currentPage - 1)"
        class="page-button"
      >
        이전
      </button>
      <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
      <button
        :disabled="currentPage === totalPages"
        @click="changePage(currentPage + 1)"
        class="page-button"
      >
        다음
      </button>
    </div>
  </div>
</template>

<script>
import { newsService } from '@/api/newsService';
import debounce from 'lodash/debounce';

export default {
  name: 'NewsSearch',
  data() {
    return {
      searchQuery: '',
      suggestions: [],
      relatedKeywords: [],
      searchResults: [],
      currentPage: 1,
      totalPages: 1,
      pageSize: 10
    };
  },
  methods: {
    // 검색어 입력 처리
    handleInput: debounce(async function() {
      if (this.searchQuery.length > 1) {
        try {
          const suggestions = await newsService.suggest(this.searchQuery);
          this.suggestions = suggestions;
        } catch (error) {
          console.error('검색어 추천 조회 실패:', error);
        }
      } else {
        this.suggestions = [];
      }
    }, 300),

    // 검색어 선택
    selectSuggestion(suggestion) {
      this.searchQuery = suggestion;
      this.suggestions = [];
      this.search();
    },

    // 검색 실행
    async search() {
      try {
        const params = {
          q: this.searchQuery,
          page: this.currentPage,
          page_size: this.pageSize
        };
        
        const response = await newsService.search(params);
        this.searchResults = response.results;
        this.totalPages = Math.ceil(response.count / this.pageSize);

        // 연관 키워드 조회
        if (this.searchQuery) {
          const keywords = await newsService.getRelatedKeywords(this.searchQuery);
          this.relatedKeywords = keywords;
        }
      } catch (error) {
        console.error('검색 실패:', error);
      }
    },

    // 키워드로 검색
    searchWithKeyword(keyword) {
      this.searchQuery = keyword;
      this.search();
    },

    // 페이지 변경
    changePage(page) {
      this.currentPage = page;
      this.search();
    },

    // 기사 조회
    async viewArticle(articleId) {
      try {
        await newsService.incrementView(articleId);
        this.$router.push(`/article/${articleId}`);
      } catch (error) {
        console.error('기사 조회 실패:', error);
      }
    },

    // 날짜 포맷팅
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
.news-search {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.search-container {
  margin-bottom: 30px;
}

.search-box {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.search-input {
  flex: 1;
  padding: 12px;
  font-size: 16px;
  border: 2px solid #ddd;
  border-radius: 8px;
}

.search-button {
  padding: 12px 24px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
}

.search-button:hover {
  background-color: #0056b3;
}

.suggestions {
  position: absolute;
  width: 100%;
  max-width: 800px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.suggestion-item {
  padding: 10px;
  cursor: pointer;
}

.suggestion-item:hover {
  background-color: #f5f5f5;
}

.related-keywords {
  margin-top: 20px;
}

.keyword-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 10px;
}

.keyword-tag {
  padding: 6px 12px;
  background-color: #e9ecef;
  border-radius: 20px;
  cursor: pointer;
  font-size: 14px;
}

.keyword-tag:hover {
  background-color: #dee2e6;
}

.article-card {
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
  margin-bottom: 20px;
}

.article-card h2 {
  margin: 0 0 10px 0;
  cursor: pointer;
  color: #007bff;
}

.article-meta {
  color: #666;
  font-size: 14px;
  margin-bottom: 10px;
}

.article-summary {
  margin: 10px 0;
  line-height: 1.5;
}

.article-tags {
  display: flex;
  gap: 8px;
  margin-top: 10px;
}

.tag {
  padding: 4px 8px;
  background-color: #e9ecef;
  border-radius: 4px;
  font-size: 12px;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  margin-top: 30px;
}

.page-button {
  padding: 8px 16px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.page-button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.page-info {
  font-size: 14px;
  color: #666;
}
</style> 