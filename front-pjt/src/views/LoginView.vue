<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import api from "@/api";

const router = useRouter();
const username = ref("");
const password = ref("");
const errorMsg = ref("");

// ✅ 로그인 요청
const login = async () => {
  try {
    const res = await api.post("/accounts/login/", {
      username: username.value,
      password: password.value,
    });

    localStorage.setItem("access", res.data.access);
    localStorage.setItem("refresh", res.data.refresh);

    api.defaults.headers.common["Authorization"] = `Bearer ${res.data.access}`;

    router.push("/dashboard");
  } catch (err) {
    errorMsg.value = err.response?.data?.detail || "로그인 실패";
  }
};

// ✅ 회원가입 이동
const goToRegister = () => {
  router.push("/register");
};
</script>

<template>
  <div class="login-container">
    <div class="login-box">
      <h2 class="login-title">
        <span>Login</span>
        <span class="login-icon">🔑</span>
      </h2>
      <form @submit.prevent="login" class="login-form">
        <input v-model="username" placeholder="아이디" class="login-input" />
        <input type="password" v-model="password" placeholder="비밀번호" class="login-input" />
        <button type="submit" class="login-button">로그인</button>
      </form>
      <p v-if="errorMsg" class="login-error">{{ errorMsg }}</p>
      <div class="register-box">
        <span>아직 회원이 아니신가요?</span>
        <button @click="goToRegister" class="register-button">회원가입</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
html, body, #app {
  height: 100%;
  margin: 0;
  padding: 0;
}
.login-container {
  min-height: 100vh;
  width: 100vw;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #fdebc8;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1;
}
.login-box {
  background: #fdebc8;
  padding: 36px 28px 28px 28px;
  border-radius: 24px;
  border: 2px solid #222;
  min-width: 320px;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 0 4px 32px rgba(0,0,0,0.10);
}
.login-title {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 24px;
  color: #222;
  display: flex;
  align-items: center;
  gap: 8px;
}
.login-icon {
  font-size: 1.5rem;
}
.login-form {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 14px;
  align-items: center;
}
.login-input {
  width: 100%;
  box-sizing: border-box;
  padding: 10px 14px;
  border: 1.5px solid #aaa;
  border-radius: 8px;
  font-size: 15px;
  outline: none;
  background: #fffbe9;
  transition: border 0.2s;
}
.login-input:focus {
  border: 2px solid #222;
}
.login-button {
  width: 90%;
  max-width: 320px;
  min-width: 180px;
  padding: 14px 0;
  background: #222;
  color: #fff;
  border: none;
  border-radius: 999px;
  font-size: 18px;
  font-weight: bold;
  cursor: pointer;
  margin-top: 8px;
  transition: background 0.2s;
  display: block;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.07);
}
.login-button:hover {
  background: #333;
}
.login-error {
  color: #ff3b3b;
  margin-top: 12px;
  font-size: 15px;
  text-align: center;
}
.register-box {
  margin-top: 22px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
}
.register-button {
  background: none;
  border: none;
  color: #222;
  font-weight: 600;
  cursor: pointer;
  padding: 0;
  font-size: 15px;
  text-decoration: underline;
}
.register-button:hover {
  color: #333833;
}
</style>
