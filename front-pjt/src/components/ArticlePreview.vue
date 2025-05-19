<!-- ArticlePreview.vue -->
<template>
  <div class="article-preview" @click="navigateToNews">
    <h3 v-if="news">{{ news.title || '제목 없음' }}</h3>
    <p v-if="news">{{ news.content?.slice(0, 100) || '내용 없음' }}...</p>
    <div v-if="news" class="article-preview-meta">
      <span>{{ news.writer || '작성자 없음' }}</span>
      <span> 🕒 {{ formatDate(news.write_date) }}</span>
    </div>
  </div>
</template>

<script setup>
import { useDate } from "@/composables/useDate";
import { useRouter } from "vue-router";

const { formatDate } = useDate();
const router = useRouter();

const props = defineProps({
  to: {
    type: String,
    required: true,
  },
  news: {
    type: Object,
    required: true,
    default: () => ({
      title: '',
      content: '',
      category: '',
      keywords: [],
      write_date: '',
      writer: '',
      url: '',
      article_interaction: { likes: 0, read: 0 },
    }),
  },
});

const navigateToNews = () => {
  console.log("navigateToNews called with path:", props.to);
  try {
    console.log("Calling router.push with path:", props.to); // 추가 로그
    router.push(props.to).then(() => {
      console.log("Navigation successful");
    }).catch(err => {
      console.error("Navigation failed:", err);
    });
  } catch (err) {
    console.error("Error in navigateToNews:", err);
  }
};
</script>

<style scoped>
.article-preview {
  padding: 10px;
  margin-bottom: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
  cursor: pointer;
}

.article-preview h3 {
  margin: 0 0 5px;
}

.article-preview p {
  margin: 0 0 5px;
  color: #666;
}

.article-preview-meta {
  font-size: 0.9em;
  color: #888;
}
</style>