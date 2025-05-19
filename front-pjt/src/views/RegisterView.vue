<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import api from "@/api";

const username = ref("");
const password = ref("");
const email = ref("");
const router = useRouter();

const handleRegister = async () => {
  try {
    await api.post("/accounts/signup/", {
      username: username.value,
      password: password.value,
      email: email.value,
    });
    alert("회원가입 성공!");
    router.push("/login");
  } catch (err) {
    alert("에러 발생: " + JSON.stringify(err.response?.data || err.message));
  }
};

// ✅ 로그인 페이지로 이동
const goToLogin = () => {
  router.push("/login");
};
</script>

<template>
  <div class="register-container">
    <div class="register-box">
      <h2 class="register-title">
        <span>Sign Up</span>
        <span class="register-icon">📝</span>
      </h2>
      <form @submit.prevent="handleRegister" class="register-form">
        <input v-model="username" placeholder="아이디" class="register-input" />
        <input v-model="email" placeholder="이메일" class="register-input" />
        <input type="password" v-model="password" placeholder="비밀번호" class="register-input" />
        <button type="submit" class="register-button-main">가입</button>
      </form>
      <div class="login-box">
        <span>이미 계정이 있으신가요?</span>
        <button @click="goToLogin" class="login-button-sub">로그인</button>
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
.register-container {
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
.register-box {
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
.register-title {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 24px;
  color: #222;
  display: flex;
  align-items: center;
  gap: 8px;
}
.register-icon {
  font-size: 1.5rem;
}
.register-form {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 14px;
  align-items: center;
}
.register-input {
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
.register-input:focus {
  border: 2px solid #222;
}
.register-button-main {
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
.register-button-main:hover {
  background: #333;
}
.login-box {
  margin-top: 22px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
}
.login-button-sub {
  background: none;
  border: none;
  color: #222;
  font-weight: 600;
  cursor: pointer;
  padding: 0;
  font-size: 15px;
  text-decoration: underline;
}
.login-button-sub:hover {
  color: #333833;
}
</style>
