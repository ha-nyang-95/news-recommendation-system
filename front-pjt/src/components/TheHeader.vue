<script setup>
import { RouterLink, useRouter } from "vue-router";
import { ref, onMounted } from "vue";

const router = useRouter();
const isLoggedIn = ref(false);

onMounted(() => {
  isLoggedIn.value = !!localStorage.getItem("access");
});

const refreshPage = (event) => {
  event.preventDefault();
  router.push("/").then(() => {
    window.location.reload();
  });
};

const handleLogout = () => {
  localStorage.removeItem("access");
  localStorage.removeItem("refresh");
  isLoggedIn.value = false;
  router.push("/login");
};
</script>

<template>
  <div class="header__container">
    <header>
      <router-link to="/" @click="refreshPage">
        <span class="logo"> SSAFYNEWS </span>
      </router-link>

      <nav class="menus">
        <router-link to="/news">나만의 뉴스 큐레이팅</router-link>
        <router-link to="/dashboard">대시보드</router-link>

        <router-link v-if="!isLoggedIn" to="/login">로그인</router-link>
        <button v-else @click="handleLogout">로그아웃</button>
      </nav>
    </header>
  </div>
</template>

<style scoped lang="scss">
.header__container {
  background-color: white;
  border-bottom: 1px solid #d4d4d4;
  header {
    max-width: 1280px;
    margin: 0 auto;
    color: black;
    height: 80px;
    justify-content: space-between;
    align-items: center;
    display: flex;
    padding: 0 15px;
  }

  .logo {
    font-size: x-large;
    font-weight: 800;
  }

  .menus {
    display: flex;
    align-items: center;
    gap: 23px;

    button {
      background: none;
      border: none;
      cursor: pointer;
      font-size: 1rem;
      color: black;

      &:hover {
        text-decoration: underline;
      }
    }
  }

  a.router-link-active {
    font-weight: bold;
  }
}
</style>
