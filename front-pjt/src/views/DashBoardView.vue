<script setup>
import { Bar, Doughnut } from "vue-chartjs";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
} from "chart.js";
import ContentBox from "@/common/ContentBox.vue";
import { ref } from "vue";
import ArticlePreview from "@/components/ArticlePreview.vue";

ChartJS.register(
  ArcElement,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend
);

const props = defineProps();

const categoryData = ref({
  labels: [],
  datasets: [
    {
      data: [],
      backgroundColor: [],
    },
  ],
});
const categories = ref([]);
const favoriteArticles = ref([]);

const keywordData = ref({
  labels: [],
  datasets: [
    {
      label: "키워드 빈도수",
      data: [],
      backgroundColor: "#C7E4B8",
    },
  ],
});

const readData = ref({
  labels: [],
  datasets: [
    {
      label: "키워드 빈도수",
      data: [],
      backgroundColor: "#DBB8E4",
    },
  ],
});

const options = {
  plugins: {
    legend: {
      display: true,
      position: "right",
      labels: {
        padding: 15,
        boxWidth: 20,
        font: {
          size: 14,
        },
      },
    },
    tooltip: {
      callbacks: {
        label: (context) => {
          const label = context.label || "";
          const value = context.raw;
          return `${label}: ${value}개`;
        },
      },
    },
    layout: {
      padding: {
        right: 40,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        min: 0,
        max: 1,
      },
    },
  },
};

const barOptions = {
  indexAxis: "y",
  scales: {
    x: {
      beginAtZero: true,
    },
  },
  plugins: {
    legend: {
      display: false,
    },
  },
};

const readBarOptions = {
  indexAxis: "x",
  scales: {
    x: {
      beginAtZero: true,
    },
  },
  plugins: {
    legend: {
      display: false,
    },
  },
};

const newsList = ref([]);
const sortBy = ref("latest");
const relatedNews = ref(null);
</script>

<template>
  <div class="dashboard">
    <h1 class="title">DASHBOARD</h1>
    <p class="subtitle">
      <br />방문 기록 및 좋아요 데이터를 기반으로 나의 관심 분야를 확인하고,
      <br />관심 분야에 맞는 기사를 추천 받아보세요. <br />여러분의 취업 여정의
      로드맵을 제공합니다.
    </p>
    <div class="layout">
      <ContentBox class="category">
        <h1>🐤 나의 관심 카테고리</h1>
        <p class="card_description">
          내가 주로 읽은 기사들을 분석하여 정치, 경제, 문화 등 가장 관심 있는
          뉴스 카테고리를 한눈에 보여드립니다.
        </p>
        <div class="category__chart">
          <Doughnut :data="categoryData" :options="options" />
          <div class="category__labels">
            <span
              v-for="(category, index) in categories"
              :key="index"
              :style="{
                borderColor: categoryData.datasets[0].backgroundColor[index],
                color: categoryData.datasets[0].backgroundColor[index],
              }"
              class="category__label"
            >
              {{ index + 1 }}순위: {{ category[0] }} ({{ category[1] }}개)
            </span>
          </div>
        </div>
      </ContentBox>

      <ContentBox class="keyword">
        <h1>⭐️ 주요 키워드</h1>
        <p class="card_description">
          내가 관심있게 본 뉴스 기사들에서 가장 많이 등장한 핵심 키워드를
          추출하여 현재 나의 주요 관심사를 보여드립니다.
        </p>
        <Bar :data="keywordData" :options="barOptions" />
      </ContentBox>
    </div>
    <div class="layout">
      <ContentBox>
        <h1>📰 주간 읽은 기사</h1>
        <p class="card_description">
          최근 일주일 동안 하루에 몇 개의 기사를 읽었는지 그래프로 확인하며 나의
          뉴스 소비 패턴을 분석합니다.
        </p>
        <Bar :data="readData" :options="readBarOptions" />
      </ContentBox>

      <ContentBox class="like-news">
        <h1>❤️ 좋아요 누른 기사</h1>
        <p class="card_description">
          내가 좋아요를 누른 기사들의 목록을 한곳에서 모아보고 다시 찾아볼 수
          있습니다.
        </p>
        <div v-for="(article, index) in favoriteArticles" :key="index">
          <ArticlePreview :to="`/news/${article.id}`" :news="article" />
        </div>
      </ContentBox>
    </div>
  </div>
</template>

<style scoped lang="scss">
.title {
  margin: 0;
  font-size: 25px;
}
.subtitle {
  font-weight: 500;
  margin-bottom: 40px;
}
.like-news {
  overflow-y: auto;
  box-sizing: border-box;
}
.dashboard {
  margin-top: 30px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.card_description {
  margin: 10px;
}

.layout {
  display: flex;
  gap: 20px;
  > * {
    height: 450px;
  }

  @media (max-width: 768px) {
    flex-direction: column;
  }
}
.category {
  &__chart {
    height: 300px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 20px;
    padding-bottom: 30px;
  }
  &__label {
    border: 1px solid;
    padding: 3px 5px;
    border-radius: 10px;
    margin-right: 10px;
  }
}

h1 {
  margin-bottom: 20px;
}
</style>
