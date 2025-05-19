<template>
  <div class="search-view">
    <h1 class="page-title">뉴스 검색</h1>
    <NewsSearch />
  </div>
</template>

<script>
import NewsSearch from '../components/NewsSearch.vue';

export default {
  name: 'SearchView',
  components: {
    NewsSearch
  }
};
</script>

<style scoped>
.search-view {
  padding: 20px;
}

.page-title {
  text-align: center;
  margin-bottom: 30px;
  color: #333;
  font-size: 2em;
}
</style> 