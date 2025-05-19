<script setup>
import StateButton from "@/common/StateButton.vue";
import { useDate } from "@/composables/useDate";
import { computed } from "vue";

const props = defineProps();

const { formatDate } = useDate();
const date = computed(() => formatDate(props.data.write_date));
</script>

<template>
  <div class="card">
    <div class="card__header">
      <StateButton type="state" size="sm" disabled>{{
        props.data.category
      }}</StateButton>
      <span class="card__header-item">{{ props.data.writer }}</span>
      <span class="card__header-item">{{ date }}</span>
    </div>
    <RouterLink :to="{ name: 'boardDetail', params: { id: props.data.id } }">
      <h2 class="title">{{ props.data.title }}</h2>
      <p class="description">{{ props.data.content }}</p>
    </RouterLink>
    <div class="tags">
      <StateButton
        v-for="(tag, index) in props.data.keywords"
        :key="index"
        type="tag"
        size="sm"
      >
        #{{ tag }}
      </StateButton>
    </div>
  </div>
</template>

<style scoped lang="scss">
.card {
  background-color: white;
  width: 80%;
  padding: 20px;
  margin-bottom: 10px;

  &__header {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.9rem;
    color: #888;

    &-item {
      font-weight: normal;
    }
  }

  .title {
    margin: 12px 0;
    font-size: 22px;
    font-weight: bold;
    color: #1c1c1e;
  }

  .description {
    font-size: 1rem;
    width: 90%;
    color: var(--c-gray-600);
    margin: 15px 0;
    display: -webkit-box;
    -webkit-line-clamp: 1;
    line-clamp: 1;
    -webkit-box-orient: vertical;
    overflow: hidden;
    text-overflow: ellipsis;
    line-height: 1.3;
  }

  .tags {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    padding-bottom: 40px;
    border-bottom: 1px solid #e7e6e6;
  }
}
</style>
