<script setup>
import { ref, onMounted, watch } from "vue";
import ContentBox from "@/common/ContentBox.vue";
import NewsCard from "@/components/NewsCard.vue";
import { tabs } from "@/assets/data/tabs";
import PaginationButton from "@/common/PaginationButton.vue";
import StateButton from "@/common/StateButton.vue";

const newsList = ref([]);
const sortBy = ref("latest");
const activeTab = ref(tabs[0].id);
const currentPage = ref(1);
const totalPages = ref(1);
const loading = ref(false);
const error = ref(null);
const searchQuery = ref("");


const fetchNews = async (search = false) => {
  try {
    loading.value = true;
    error.value = null;

    const selectedTab = tabs.find(tab => tab.id === activeTab.value);
    const categoryValue = selectedTab ? selectedTab.value : "";

    const params = new URLSearchParams({
      q: search ? searchQuery.value : '',
      page: currentPage.value,
      size: 10,
      sort: sortBy.value,
      category: categoryValue,
    });
    const url = `http://localhost:8000/api/news/search/?${params.toString()}`;
    console.log("Fetching news from:", url);

    const res = await fetch(url);
    if (!res.ok) {
      const errorData = await res.json();
      throw new Error(errorData.error || `서버 오류: ${res.status}`);
    }
    const json = await res.json();

    if (!json.results || !Array.isArray(json.results)) {
      throw new Error("응답 데이터 형식이 올바르지 않습니다: 'results' 배열이 누락됨");
    }

    newsList.value = json.results.map((item) => ({
      ...item,
      writer: item.writer || '알 수 없음',
      write_date: item.write_date || '',
      article_interaction: item.article_interaction ?? { likes: 0, read: 0 },
    }));
    totalPages.value = Math.ceil(json.total / json.size);
  } catch (err) {
    error.value = err.message;
    newsList.value = [];
    console.error("🚨 뉴스 데이터를 불러오는 데 실패했습니다:", err);
  } finally {
    loading.value = false;
  }
};

const searchNews = async () => {
  currentPage.value = 1;
  await fetchNews(true);
};

onMounted(() => fetchNews());
watch([currentPage, sortBy, activeTab], () => {
  fetchNews();
});
</script>

<template>
  <div class="news">
    <div>
      <h1 class="news__title">🤖 AI 맞춤 추천 뉴스</h1>
      <p class="news__description">
        당신이 원하는 뉴스, 이제 AI가 직접 추천해드립니다!<br />
        나만의 취향을 기반으로, 맞춤형 뉴스만 쏙쏙 골라주는<br />
        뉴스 큐레이팅 서비스
        <strong style="font-weight: bold">SSAFYNEWS</strong>에 빠져보세요.
        <br />AI 챗봇과 기사에 대해 대화하며 궁금한 점을 물어보고, <br />한눈에
        보기 쉬운 대시보드를 통해 나의 뉴스 소비 패턴도 확인할 수 있습니다.
      </p>

      <div class="search-container" style="display: flex; gap: 12px; margin: 20px 0;">
        <input
          v-model="searchQuery"
          @keyup.enter="searchNews"
          placeholder="검색어를 입력하세요"
          class="search-input"
          style="flex: 1; padding: 12px 16px; border: 1px solid #ccc; border-radius: 8px; font-size: 15px;"
        />
        <button
          @click="searchNews"
          class="search-button"
          style="padding: 12px 24px; background-color: #272c97; color: white; border: none; border-radius: 8px; font-weight: 600; cursor: pointer;"
        >
          검색
        </button>
      </div>


      <ContentBox class="news__tabs">
        <StateButton
          v-for="tab in tabs"
          :key="tab.id"
          type="state"
          :is-active="activeTab === tab.id"
          @click="activeTab = tab.id"
        >
          {{ tab.label }}
        </StateButton>
      </ContentBox>
    </div>

    <ContentBox class="news__box">
      <div class="news__box__title-container">
        <div class="filters__container">
          <select class="filters" v-model="sortBy">
            <option value="latest">최신순</option>
            <option value="oldest">오래된순</option>
          </select>
        </div>
      </div>

      <div v-if="loading" class="news__box__noti">로딩 중...</div>
      <div v-else-if="error" class="news__box__noti error">{{ error }}</div>
      <div v-else class="news__box__cards">
        <div v-if="!newsList || newsList.length === 0" class="news__box__noti">뉴스가 없습니다.</div>
        <div v-else>
          <NewsCard
            v-for="news in newsList"
            :key="news.id"
            :data="news"
            :to="`/news/${news.id}`"
          />
        </div>
      </div>

      <PaginationButton v-model="currentPage" :totalPages="totalPages" />
    </ContentBox>
  </div>
</template>

<style scoped lang="scss">
.news {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-top: 30px;

  &__title {
    font-size: 20px;
    font-weight: 700;
    border-bottom: 1px solid #e2e2e2;
    padding-bottom: 10px;
  }

  &__description {
    font-size: 16px;
    font-weight: 400;
    color: #575757;
    line-height: normal;
    margin: 15px 0 25px;

    &--job {
      color: red;
      margin-bottom: 20px;
    }
  }

  &__tabs {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    padding: 12px 30px !important;
  }

  &__box {
    padding: 30px !important;

    &__noti {
      color: #666666;
      font-size: 12px;
      padding: 5px 10px;
      text-align: center;

      &.error {
        color: #ff0000;
      }
    }

    &__title-container {
      position: relative;
      display: flex;
      align-items: center;
    }

    &__title {
      font-weight: 700;
      font-size: 21px;
      cursor: pointer;

      &-username {
        font-weight: 400;
        padding: 3px;
        border-bottom: 2px solid #272c97;
      }
      &-icon {
        font-size: 15px;
      }
    }

    &__subtitle-loggedin {
      font-weight: 400;
      padding: 10px 0 0 10px;
      color: #575757;
      opacity: 0;
      transition: opacity 0.3s ease;
      pointer-events: none;
      text-decoration: underline;
    }

    &__title-container:hover .news__box__subtitle-loggedin {
      opacity: 1;
    }

    .filters__container {
      position: absolute;
      right: 0;
    }

    &__cards {
      margin-top: 30px;
      margin-left: 30px;
      display: flex;
      flex-direction: column;
      gap: 20px;
    }

    .search-bar {
      display: flex;
      gap: 10px;
      margin-bottom: 20px;

      input {
        flex: 1;
        font-size: 14px;
      }

      button {
        white-space: nowrap;
      }
    }

  }
}
</style>