<script setup>
import { ref, onMounted } from "vue";
import ContentBox from "@/common/ContentBox.vue";
import StateButton from "@/common/StateButton.vue";
import { useDate } from "@/composables/useDate";
import router from "@/router";
import LeftArrow from "@/components/icon/LeftArrow.svg";
import ArticlePreview from "@/components/ArticlePreview.vue";

const news = ref(null);
const relatedNews = ref([]);
const loading = ref(true);
const error = ref(null);

const { formatDate } = useDate();

const liked = ref(false);
const likeCount = ref(0);
const isAnimating = ref(false);

const fetchNewsDetail = async (newsId) => {
  try {
    loading.value = true;
    console.log("Fetching news for ID:", newsId);
    const res = await fetch(`http://localhost:8000/api/news/${newsId}`);
    console.log("Response status:", res.status);
    if (!res.ok) {
      const errorData = await res.json();
      throw new Error(errorData.error || "뉴스 데이터를 가져오지 못했습니다.");
    }
    const json = await res.json();
    console.log("News data:", json);
    news.value = {
      ...json,
      article_interaction: json.article_interaction ?? { likes: 0, read: 0 },
    };

    const relatedRes = await fetch(`http://localhost:8000/api/news/${newsId}/recommend/`);
    console.log("Related news response status:", relatedRes.status);
    if (!relatedRes.ok) {
      const errorData = await relatedRes.json();
      throw new Error(errorData.error || "관련 뉴스를 가져오지 못했습니다.");
    }
    const relatedData = await relatedRes.json();
    console.log("Related news data:", relatedData);
    relatedNews.value = Array.isArray(relatedData)
      ? relatedData.map(item => ({
          ...item,
          title: item.title || '제목 없음',
          content: item.content || '내용 없음',
          writer: item.writer || '작성자 없음',
          write_date: item.write_date || '',
          article_interaction: item.article_interaction ?? { likes: 0, read: 0 },
        }))
      : [];
  } catch (err) {
    error.value = err.message;
    console.error("🚨 뉴스 데이터를 불러오는 데 실패했습니다:", err);
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  const newsId = router.currentRoute.value.params.id;
  if (newsId) {
    fetchNewsDetail(newsId);
  }
});
</script>

<template>
  <div id="news-detail-container">
    <button @click="() => router.back()" class="back-btn">
      <img :src="LeftArrow" alt="Back Arrow" />
    </button>
    <div v-if="loading" class="loading">로딩 중...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="news" class="news-detail">
      <div class="article__container">
        <ContentBox>
          <div class="article">
            <div class="article__header">
              <StateButton type="state" size="sm" isActive disabled>{{ news.category }}</StateButton>
              <h2 class="article__header-title">{{ news.title }}</h2>
              <div class="article__header-writer">
                <span>{{ news.writer }}</span>
                <span> 🕒 {{ formatDate(news.write_date) }}</span>
              </div>
            </div>

            <p class="article__content">{{ news.content }}</p>

            <div class="article__tags">
              <StateButton
                v-for="(tag, index) in news.keywords"
                :key="index"
                type="tag"
                size="sm"
              >
                {{ tag }}
              </StateButton>
            </div>

            <div class="article__content__footer">
              <div class="article__content__emoji">
                <span class="emoji-btn">
                  <span v-if="liked"> ❤️ </span> <span v-else>🤍</span>{{ likeCount }}
                </span>
                <div class="emoji-btn">
                  <span class="content__emoji-eye"> 👀 </span>{{ news.article_interaction?.read || 0 }}
                </div>
                <a :href="news.url">📄</a>
              </div>
              <button class="emoji-btn">
                <span>{{ liked ? "❤️" : "🤍" }} 좋아요</span>
              </button>
              <transition name="heart-float">
                <span v-if="isAnimating" class="floating-heart">
                  {{ liked ? "❤️" : "🤍" }}
                </span>
              </transition>
            </div>
          </div>
        </ContentBox>
      </div>

      <ContentBox class="sidebar">
        <h1 class="sidebar__title">📰 관련 기사</h1>
        <div v-if="relatedNews.length === 0" class="news__box__noti">관련 기사가 없습니다.</div>
        <div v-else class="news__box__cards">
          <ArticlePreview
            v-for="(newsItem, index) in relatedNews"
            :key="index"
            :to="`/news/${newsItem.id}`"
            :news="newsItem"
          />
        </div>
      </ContentBox>
    </div>
  </div>
</template>

<style scoped lang="scss">
/* 스타일은 기존과 동일 */
</style>