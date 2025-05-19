<script setup>
import { ref, computed, useAttrs, defineProps } from "vue";

defineOptions({
  inheritAttrs: false,
});

const props = defineProps();
const wrapperClass = computed(() => props.wrapperClass || "");
const value = computed(() => props.value || "");
const modelValue = ref("");

const attrs = useAttrs();

const errorClass = computed(() => {
  return props.error ? "error" : "";
});
</script>

<template>
  <div :class="['input-box', wrapperClass, errorClass]">
    <input type="text" v-model="modelValue" v-bind="attrs" />
  </div>
  <p class="error-msg">{{ props.error }}</p>
</template>

<style scoped lang="scss">
.input-box {
  width: 100%;
  padding: 5px 8px;
  border: 1px solid #e5e5ea;
  border-radius: 8px;
  display: flex;
  align-items: center;

  &.error {
    border-color: var(--c-error);
  }

  input {
    width: 100%;
    border: none;
    outline: none;
    background-color: transparent;
    color: #333;
    padding: 6px;

    &::placeholder {
      color: #aaa;
    }

    &:disabled::placeholder {
      color: var(--c-text);
    }
  }
}

.error-msg {
  position: absolute;
  color: var(--c-error);
  margin: 5px 0 0 5px;
  font-size: 12px;
}
</style>
